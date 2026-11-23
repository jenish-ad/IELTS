import unittest
from unittest.mock import patch

from app.services.feedback import assess_text


class FakeLoader:
    def generate(self, messages, max_new_tokens):
        self.messages = messages
        return '{"corrected_text":"I enjoy reading.","grammar_errors":[],"feedback":{"strengths":["Clear answer"],"improvements":[],"next_steps":["Add an example"]},"estimated_bands":{"grammar":6.0,"lexical_resource":6.0,"coherence":6.0}}'


class FeedbackTests(unittest.TestCase):
    @patch("app.services.feedback.QWEN_ENABLED", True)
    def test_assess_text_returns_structured_feedback(self):
        result = assess_text("What do you enjoy?", "I enjoy reading.", FakeLoader())
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["corrected_text"], "I enjoy reading.")

    @patch("app.services.feedback.QWEN_ENABLED", True)
    def test_extracts_json_wrapped_in_model_text(self):
        loader = FakeLoader()
        loader.generate = lambda messages, max_new_tokens: "Here is the result: " + FakeLoader().generate(messages, max_new_tokens)
        result = assess_text("Question", "Answer", loader)
        self.assertEqual(result["status"], "completed")

    @patch("app.services.feedback.QWEN_ENABLED", False)
    def test_disabled_mode_does_not_load_model(self):
        result = assess_text("Question", "Answer", FakeLoader())
        self.assertEqual(result["status"], "disabled")


if __name__ == "__main__":
    unittest.main()
