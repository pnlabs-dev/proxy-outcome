import json
import unittest

from proxy_outcome import Attribution, Outcome, classify


class ClassifierTests(unittest.TestCase):
    def test_2xx_is_success(self):
        result = classify(status_code=200)
        self.assertEqual(result.outcome, Outcome.SUCCESS)
        self.assertEqual(result.attribution, Attribution.NONE)
        self.assertFalse(result.proxy_endpoint_health_evidence)

    def test_3xx_is_redirect_not_usable_success(self):
        result = classify(status_code=302)
        self.assertEqual(result.outcome, Outcome.HTTP_REDIRECT)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_403_does_not_invent_root_cause(self):
        result = classify(status_code=403)
        self.assertEqual(result.outcome, Outcome.HTTP_ACCESS_DENIED)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertFalse(result.proxy_layer_evidence)
        self.assertFalse(result.proxy_endpoint_health_evidence)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_429_is_observed_rate_limit_without_root_cause_claim(self):
        result = classify(status_code=429, headers={"Retry-After": "60"})
        self.assertEqual(result.outcome, Outcome.HTTP_RATE_LIMIT)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertIn("Retry-After present", result.evidence)
        self.assertFalse(result.proxy_endpoint_health_evidence)

    def test_451_is_legal_restriction_not_geo_claim(self):
        result = classify(status_code=451)
        self.assertEqual(result.outcome, Outcome.HTTP_LEGAL_RESTRICTION)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_other_4xx_remains_origin_ambiguous(self):
        result = classify(status_code=404)
        self.assertEqual(result.outcome, Outcome.HTTP_OTHER_4XX)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)

    def test_407_is_proxy_auth_but_not_endpoint_health_or_rotation_signal(self):
        result = classify(status_code=407)
        self.assertEqual(result.outcome, Outcome.PROXY_AUTH_FAILURE)
        self.assertEqual(result.attribution, Attribution.PROXY)
        self.assertTrue(result.proxy_layer_evidence)
        self.assertFalse(result.proxy_endpoint_health_evidence)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_expired_proxy_auth_text_is_not_endpoint_health_signal(self):
        result = classify(error="454 Proxy Authentication Expired")
        self.assertEqual(result.outcome, Outcome.PROXY_AUTH_FAILURE)
        self.assertTrue(result.proxy_layer_evidence)
        self.assertFalse(result.proxy_endpoint_health_evidence)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_proxy_authenticate_header_name_is_signal_without_value_echo(self):
        secret = "Basic SECRET-DO-NOT-LEAK"
        result = classify(headers={"Proxy-Authenticate": secret})
        self.assertEqual(result.outcome, Outcome.PROXY_AUTH_FAILURE)
        self.assertTrue(result.proxy_layer_evidence)
        serialized = json.dumps(result.to_dict())
        self.assertNotIn(secret, serialized)
        self.assertNotIn("SECRET-DO-NOT-LEAK", serialized)

    def test_header_values_are_not_used_for_token_matching(self):
        result = classify(
            status_code=403,
            headers={"X-Debug": "proxy authentication expired"},
        )
        self.assertEqual(result.outcome, Outcome.HTTP_ACCESS_DENIED)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)

    def test_proxy_connection_error_is_path_failure_not_bad_endpoint_claim(self):
        result = classify(error="net::ERR_PROXY_CONNECTION_FAILED")
        self.assertEqual(result.outcome, Outcome.PROXY_PATH_FAILURE)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertTrue(result.proxy_layer_evidence)
        self.assertFalse(result.proxy_endpoint_health_evidence)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_dedicated_endpoint_probe_can_support_rotation(self):
        result = classify(endpoint_probe_failed=True)
        self.assertEqual(result.outcome, Outcome.PROXY_ENDPOINT_UNHEALTHY)
        self.assertEqual(result.attribution, Attribution.PROXY)
        self.assertTrue(result.proxy_layer_evidence)
        self.assertTrue(result.proxy_endpoint_health_evidence)
        self.assertTrue(result.automatic_rotation_evidence)

    def test_503_does_not_invent_upstream_origin(self):
        result = classify(status_code=503)
        self.assertEqual(result.outcome, Outcome.HTTP_5XX)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertFalse(result.proxy_endpoint_health_evidence)
        self.assertFalse(result.automatic_rotation_evidence)

    def test_unknown_timeout_is_ambiguous(self):
        result = classify(error="request timeout")
        self.assertEqual(result.outcome, Outcome.AMBIGUOUS)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertFalse(result.proxy_layer_evidence)

    def test_challenge_hint_does_not_change_root_cause_attribution(self):
        result = classify(status_code=403, body_hint="Cloudflare challenge")
        self.assertEqual(result.outcome, Outcome.HTTP_ACCESS_DENIED)
        self.assertEqual(result.attribution, Attribution.AMBIGUOUS)
        self.assertIn("challenge/access-control hint present", result.evidence)

    def test_raw_header_values_are_not_emitted(self):
        secret = "Bearer SECRET-DO-NOT-LEAK"
        result = classify(
            status_code=429,
            headers={"Authorization": secret, "Retry-After": "60"},
        )
        serialized = json.dumps(result.to_dict())
        self.assertNotIn(secret, serialized)
        self.assertNotIn("SECRET-DO-NOT-LEAK", serialized)


if __name__ == "__main__":
    unittest.main()
