import pytest
import pytest_check as check
from pytest_mock import MockerFixture

from hippogym.hippogym import HippoGym
from hippogym.trial import TrialConfig, Trial
from hippogym.trialsteps import TrialStep

from tests.fakes import FakeProcess


class TestHippoGym:
    """HippoGym"""

    @pytest.fixture(autouse=True)
    def setup(self, mocker: MockerFixture):
        self.process_patch = mocker.patch("hippogym.hippogym.Process", mocker.Mock)
        self.trial = mocker.Mock()
        self.trial_config = mocker.Mock()
        self.trial_config.sample = lambda _: self.trial
        self.hippo = HippoGym(self.trial_config)

    def test_init_trialstep(self, mocker: MockerFixture):
        """should be able to initialize from a TrialStep"""
        trial_step = mocker.Mock()
        trial_step.__class__ = TrialStep
        hippo = HippoGym(trial_step)
        check.is_instance(hippo.trial_config, TrialConfig)

    def test_init_trial(self, mocker: MockerFixture):
        """should be able to initialize from a Trial"""
        trial_step = mocker.Mock()
        trial_step.__class__ = Trial
        hippo = HippoGym(trial_step)
        check.is_instance(hippo.trial_config, TrialConfig)

    def test_start_trial(self, mocker: MockerFixture):
        """should start a new Trial for the given user"""
        mocker.patch("hippogym.hippogym.Process", FakeProcess)
        self.hippo.start_trial("fake_user")
        check.equal(len(self.hippo.trials), 1)
        check.is_true(self.trial.run.called)

    def test_start_trial_user_conflict(self, mocker: MockerFixture):
        """should raise if given user is already in trial"""
        self.hippo.trials["fake_user"] = mocker.Mock()
        with pytest.raises(ValueError):
            self.hippo.start_trial("fake_user")

    def test_stop_trial(self, mocker: MockerFixture):
        """should stop the current Trial for the given user"""
        process_patch = mocker.Mock()
        self.hippo.trials["fake_user"] = process_patch
        self.hippo.stop_trial("fake_user")
        check.equal(len(self.hippo.trials), 0)
        check.is_true(process_patch.terminate.called)
        check.is_true(process_patch.close.called)
