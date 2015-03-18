""" Interface specification defining the methods needed for using the different
classes of algorithms present in the framework

@author: Jerker Nordh
"""
import abc
import numpy

class SIR():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def measure(self, particles, y, t):
        pass

    @abc.abstractmethod
    def qsample(self, particles, u, y, t):
        pass

    @abc.abstractmethod
    def logp_q(self, particles, next_part, u, y, t):
        pass

    @abc.abstractmethod
    def logp_xnext(self, particles, next_part, u, t):
        pass

    @abc.abstractmethod
    def create_initial_estimate(self, N):
        """Sample particles from initial distribution

        Args:
         - N (int): Number of particles to sample

        Returns:
         (array-like) with first dimension = N, model specific representation
         of all particles """
        pass

    def copy_ind(self, particles, new_ind=None):
        """
        Copy select particles, can be overriden for models that require
        special handling of the particle representations when copying them

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - new_ind (array-like): Array of ints, specifying indices to copy

        Returns:
         (array-like) with first dimension = len(new_ind)
        """
        if (new_ind != None):
            return numpy.copy(particles[new_ind])
        else:
            return numpy.copy(particles)

    def sample_smooth(self, part, ptraj, anc, future_trajs, find, ut, yt, tt, cur_ind):
        return numpy.copy(part)


class ParticleFilteringNonMarkov():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def update_full(self, particles, traj, uvec, yvec, tvec, ancestors, noise):
        pass

    @abc.abstractmethod
    def measure_full(self, particles, traj, uvec, yvec, tvec, ancestors):
        pass

    @abc.abstractmethod
    # TODO: yt should be included here
    def sample_process_noise_full(self, ptraj, ancestors, ut, tt):
        """
        Sample process noise

        Args:
         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - u (array-like):  input signal
         - t (float): time-stamp

        Returns:
         (array-like) with first dimension = N
        """
        pass

    @abc.abstractmethod
    def create_initial_estimate(self, N):
        """Sample particles from initial distribution

        Args:
         - N (int): Number of particles to sample

        Returns:
         (array-like) with first dimension = N, model specific representation
         of all particles """
        pass

    def copy_ind(self, particles, new_ind=None):
        """
        Copy select particles, can be overriden for models that require
        special handling of the particle representations when copying them

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - new_ind (array-like): Array of ints, specifying indices to copy

        Returns:
         (array-like) with first dimension = len(new_ind)
        """
        if (new_ind != None):
            return numpy.copy(particles[new_ind])
        else:
            return numpy.copy(particles)


    def sample_smooth(self, part, ptraj, anc, future_trajs, find, ut, yt, tt, cur_ind):
        """
        Create sampled estimates for the smoothed trajectory. Allows the update
        representation of the particles used in the forward step to include
        additional data in the backward step, can also for certain models be
        used to update the points estimates based on the future information.

        Default implementation uses the same format as forward in time it
        ss part of the ParticleFiltering interface since it is used also when
        calculating "ancestor" trajectories

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - future_trajs (array-like): particle estimate for {t+1:T}
         - ut (array-like): input signals for {t:T}
         - yt (array-like): measurements for {t:T}
         - tt (array-like): time stamps for {t:T}

        Returns:
         (array-like) with first dimension = N
        """
        # default implementation uses the same format as forward in time
        # Is part of the ParticleFiltering interface since it is used
        # also when calculating "ancestor trajectories"
        return numpy.copy(part)


class ParticleFiltering(ParticleFilteringNonMarkov):
    """
    Base class for particles to be used with particle filtering.
    particles are a model specific array where the first dimension
    indexes the different particles.
    """
    __metaclass__ = abc.ABCMeta

    def sample_process_noise_full(self, ptraj, ancestors, ut, tt):
        return self.sample_process_noise(particles=ptraj[-1].pa.part[ancestors],
                                         u=ut[-1], t=tt[-1])

    def update_full(self, particles, traj, uvec, yvec, tvec, ancestors, noise):
        return self.update(particles=particles, u=uvec[-1], t=tvec[-1], noise=noise)

    def measure_full(self, particles, traj, uvec, yvec, tvec, ancestors):
        return self.measure(particles, y=yvec[-1], t=tvec[-1])

    @abc.abstractmethod
    def sample_process_noise(self, particles, u, t):
        pass

    @abc.abstractmethod
    def update(self, particles, u, t, noise):
        """ Propagate estimate forward in time

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - u (array-like):  input signal
         - t (float): time-stamp
         - noise (array-like): noise realization used for the calucations
           , with first dimension = N (number of particles)

        Returns:
         (array-like) with first dimension = N, particle estimate at time t+1
        """
        pass

    @abc.abstractmethod
    def measure(self, particles, y, t):
        """
        Return the log-pdf value of the measurement

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - y (array-like):  measurement
         - t (float): time-stamp

        Returns:
         (array-like) with first dimension = N, logp(y|x^i)
        """
        pass



class AuxiliaryParticleFiltering(object):
    """
    Base class for particles to be used with auxiliary particle filtering
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def eval_1st_stage_weights(self, particles, u, y, t):
        """
        Evaluate "first stage weights" for the auxiliary particle filter.
        (log-probability of measurement using some propagated statistic, such
        as the mean, for the future state)

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - u (array-like): input signal
         - y (array-like):  measurement
         - t (float): time-stamp

        Returns:
         (array-like) with first dimension = N, logp(y_{t+1}|\hat{x}_{t+1|t}^i)
        """
        pass

class FFBSiNonMarkov(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def logp_xnext_full(self, part, past_trajs, pind, future_trajs, find, ut, yt, tt, cur_ind):
        pass

    @abc.abstractmethod
    def logp_xnext_singlestep(self, part, past_trajs, pind, future_parts, find, ut, yt, tt, cur_ind):
        pass

class FFProposeFromMeasure(FFBSiNonMarkov):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def propose_from_y(self, N, y, t):
        """
        Create N particles from p(x_t|y_t)
        """
        pass


class FFBSi(FFBSiNonMarkov):
    """
    Base class for particles to be used with particle smoothing
    (Backward Simulation)
    """
    __metaclass__ = abc.ABCMeta

    def logp_xnext_full(self, part, past_trajs, pind,
                        future_trajs, find, ut, yt, tt, cur_ind):
        """
        Return the log-pdf value for the entire future trajectory.
        Useful for non-markovian modeles, that result from e.g
        marginalized state-space models.

        Default implemention just calls logp_xnext which is enough for
        Markovian models

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - future_trajs (array-like): particle estimate for {t+1:T}
         - ut (array-like): input signals for {t:T}
         - yt (array-like): measurements for {t:T}
         - tt (array-like): time stamps for {t:T}

        Returns:
         (array-like) with first dimension = N, logp(x_{t+1:T}|x_t^i)
        """

        # Default implemenation for markovian models, just look at the next state
        return self.logp_xnext(particles=part, next_part=future_trajs[0].pa.part[find],
                               u=ut[cur_ind], t=tt[cur_ind])

    def logp_xnext_singlestep(self, part, past_trajs, pind,
                              future_parts, find, ut, yt, tt, cur_ind):
        """
        Return the log-pdf value for the entire future trajectory.
        Useful for non-markovian modeles, that result from e.g
        marginalized state-space models.

        Default implemention just calls logp_xnext which is enough for
        Markovian models

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - future_trajs (array-like): particle estimate for {t+1:T}
         - ut (array-like): input signals for {t:T}
         - yt (array-like): measurements for {t:T}
         - tt (array-like): time stamps for {t:T}

        Returns:
         (array-like) with first dimension = N, logp(x_{t+1:T}|x_t^i)
        """

        # Default implemenation for markovian models, just look at the next state
        return self.logp_xnext(particles=part, next_part=future_parts[find],
                               u=ut[cur_ind], t=tt[cur_ind])

    @abc.abstractmethod
    def logp_xnext(self, particles, next_part, u, t):
        """
        Return the log-pdf value for the possible future state 'next'
        given input u

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - next_part (array-like): particle estimate for t+1
         - u (array-like): input signal
         - t (float): time stamps

        Returns:
         (array-like) with first dimension = N, logp(x_{t+1}|x_t^i)
        """
        pass

class FFBSiRSNonMarkov(FFBSiNonMarkov):
    """
    Base class for models to be used with rejection sampling methods
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def logp_xnext_max_full(self, part, past_trajs, pind, uvec, yvec, tvec, cur_ind):
        """
        Return the max log-pdf value for all possible future states'
        given input u

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - next_part (array-like): particle estimate for t+1
         - u (array-like): input signal
         - t (float): time stamps

        Returns:
         (array-like) with first dimension = N, argmax_{x_{t+1}} logp(x_{t+1}|x_t)
        """
        pass

class FFBSiRS(FFBSi):
    """
    Base class for models to be used with rejection sampling methods
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def logp_xnext_max(self, particles, u, t):
        """
        Return the max log-pdf value for all possible future states'
        given input u

        Args:

         - particles  (array-like): Model specific representation
           of all particles, with first dimension = N (number of particles)
         - next_part (array-like): particle estimate for t+1
         - u (array-like): input signal
         - t (float): time stamps

        Returns:
         (array-like) with first dimension = N, argmax_{x_{t+1}} logp(x_{t+1}|x_t)
        """
        pass


    def logp_xnext_max_full(self, part, past_trajs, pind, uvec, yvec, tvec, cur_ind):
        return self.logp_xnext_max(part, u=uvec[cur_ind], t=tvec[cur_ind])

class SampleProposer(object):
    """
    Base class for models to be used with methods that require drawing of new
    samples. Here 'q' is the name we give to the proposal distribtion.
    """
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def propose_smooth(self, ptraj, anc, future_trajs, find, yt, ut, tt, cur_ind):
        """
        Sample from a distribution q(x_t | x_{t-1}, x_{t+1:T}, y_t:T)

        Args:
         - partp (array-like): particle estimate of t-1
         - up (array-like): input signal at time t-1
         - tp (float): time stamp for time t-1
         - ut (array-like): input signal at time t
         - yt (array-like): measurement at time t
         - tt (array-like): time stamps for {t+1:T}
         - future_trajs (array-like): particle estimate for {t+1:T}

        Returns:
         (array-like) of dimension N, wher N is the dimension of partp and/or
         future_trajs (one of which may be 'None' at the start/end of the dataset)
        """
        pass

    @abc.abstractmethod
    def logp_proposal(self, prop_part, ptraj, anc, future_trajs, find, yt, ut, tt, cur_ind):
        """
        Eval the log-propability of the proposal distribution

        Args:
         - prop_part (array-like): Proposed particle estimate, first dimension
           has length = N
         - partp (array-like): particle estimate of t-1
         - up (array-like): input signal at time t-1
         - tp (float): time stamp for time t-1
         - ut (array-like): input signal at time t
         - yt (array-like): measurement at time t
         - tt (array-like): time stamps for {t+1:T}
         - future_trajs (array-like): particle estimate for {t+1:T}

        Returns
         (array-like) with first dimension = N,
         log q(x_t | x_{t-1}, x_{t+1:T}, y_t:T)
        """
        pass
