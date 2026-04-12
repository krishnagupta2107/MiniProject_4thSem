import pytest
from app.services.match_service import _get_label, _check_experience

class TestMatchingLogic:
    
    def test_get_label_shortlist(self):
        """Candidates >= 70 score must strictly securely classify as Shortlisted."""
        assert _get_label(85.0) == "Shortlisted"
        assert _get_label(70.0) == "Shortlisted"

    def test_get_label_maybe(self):
        """Candidates >= 45 and < 70 score classify as Maybe."""
        assert _get_label(55.0) == "Maybe"
        assert _get_label(45.0) == "Maybe"

    def test_get_label_rejected(self):
        """Candidates < 45 score strictly classify as Rejected."""
        assert _get_label(44.9) == "Rejected"
        assert _get_label(20.0) == "Rejected"
        
    def test_check_experience_bonus_multiplier(self):
        """Test experience scaling calculations against JD requirements."""
        # Underqualified
        assert _check_experience(candidate_yrs=1.0, jd_yrs=5.0) == 0.0
        
        # Perfect fit
        assert _check_experience(candidate_yrs=5.0, jd_yrs=5.0) == 1.0
        
        # Generous Overqualified limits
        assert _check_experience(candidate_yrs=8.0, jd_yrs=2.0) == 1.0
        
        # Handling edge cases without blowing up the math multiplier
        assert _check_experience(candidate_yrs=0.0, jd_yrs=0.0) == 0.5
