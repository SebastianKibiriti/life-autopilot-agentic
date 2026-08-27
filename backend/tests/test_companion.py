import unittest

from app.campus import resolve_campus
from app.companion import CompanionMemory, create_fitness_suggestion
from app.models import CompanionProfile


class CompanionMemoryTests(unittest.TestCase):
    def test_campus_alias_resolution_and_unknown_place(self):
        self.assertEqual(resolve_campus("Nutrition 204").canonical_name, "Nutrition Building N204")
        self.assertIsNone(resolve_campus("Unverified Room X"))

    def test_profile_is_user_scoped_and_suggestion_retains_followups(self):
        memory = CompanionMemory()
        profile = CompanionProfile(student_id="student-a", preferred_activities=["cycling"])
        memory.save_profile(profile)
        self.assertEqual(memory.profile("student-b").preferred_activities, [])
        suggestion = memory.save_suggestion(create_fitness_suggestion("student-a", memory.profile("student-a")))
        self.assertIn("alternatives", suggestion.follow_up_answers)
        self.assertIsNone(memory.get_suggestion("student-b", suggestion.id))

    def test_malformed_gemini_followups_are_normalized(self):
        suggestion = create_fitness_suggestion("student-a", CompanionProfile(student_id="student-a"), generated={"follow_up_answers": ["What is the optimal duration?"]})
        self.assertIsInstance(suggestion.follow_up_answers, dict)
        self.assertIn("duration", suggestion.follow_up_answers)

    def test_invalid_gemini_payload_uses_safe_defaults(self):
        suggestion = create_fitness_suggestion("student-a", CompanionProfile(student_id="student-a"), generated=["not an object"])
        self.assertIn("why", suggestion.follow_up_answers)


if __name__ == "__main__":
    unittest.main()
