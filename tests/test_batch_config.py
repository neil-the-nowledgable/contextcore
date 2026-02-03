"""Tests for OTel batch processor configuration diagnostics."""

import logging
import os
import unittest
from unittest.mock import patch

from contextcore.compat.otel_batch_config import (
    BSP_EXPORT_TIMEOUT_MS,
    BSP_MAX_EXPORT_BATCH_SIZE,
    BSP_MAX_QUEUE_SIZE,
    BSP_SCHEDULE_DELAY_MS,
    BLRP_EXPORT_TIMEOUT_MS,
    BLRP_MAX_EXPORT_BATCH_SIZE,
    BLRP_MAX_QUEUE_SIZE,
    BLRP_SCHEDULE_DELAY_MS,
    get_batch_config_summary,
    log_batch_config,
)


class TestGetBatchConfigSummary(unittest.TestCase):
    """Tests for get_batch_config_summary()."""

    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_when_no_env_vars(self):
        """All values should report defaults when no env vars are set."""
        summary = get_batch_config_summary()

        # Span processor defaults
        self.assertEqual(summary["OTEL_BSP_SCHEDULE_DELAY"]["value"], BSP_SCHEDULE_DELAY_MS)
        self.assertEqual(summary["OTEL_BSP_MAX_QUEUE_SIZE"]["value"], BSP_MAX_QUEUE_SIZE)
        self.assertEqual(summary["OTEL_BSP_MAX_EXPORT_BATCH_SIZE"]["value"], BSP_MAX_EXPORT_BATCH_SIZE)
        self.assertEqual(summary["OTEL_BSP_EXPORT_TIMEOUT"]["value"], BSP_EXPORT_TIMEOUT_MS)

        # Log processor defaults
        self.assertEqual(summary["OTEL_BLRP_SCHEDULE_DELAY"]["value"], BLRP_SCHEDULE_DELAY_MS)
        self.assertEqual(summary["OTEL_BLRP_MAX_QUEUE_SIZE"]["value"], BLRP_MAX_QUEUE_SIZE)
        self.assertEqual(summary["OTEL_BLRP_MAX_EXPORT_BATCH_SIZE"]["value"], BLRP_MAX_EXPORT_BATCH_SIZE)
        self.assertEqual(summary["OTEL_BLRP_EXPORT_TIMEOUT"]["value"], BLRP_EXPORT_TIMEOUT_MS)

        # None should be marked customized
        for entry in summary.values():
            self.assertFalse(entry["customized"])

    @patch.dict(os.environ, {"OTEL_BSP_SCHEDULE_DELAY": "1000"}, clear=True)
    def test_custom_env_var_reflected(self):
        """A set env var should appear with its custom value and customized=True."""
        summary = get_batch_config_summary()

        bsp_delay = summary["OTEL_BSP_SCHEDULE_DELAY"]
        self.assertEqual(bsp_delay["value"], 1000)
        self.assertTrue(bsp_delay["customized"])
        self.assertEqual(bsp_delay["default"], BSP_SCHEDULE_DELAY_MS)

    @patch.dict(
        os.environ,
        {
            "OTEL_BSP_MAX_QUEUE_SIZE": "8192",
            "OTEL_BLRP_MAX_EXPORT_BATCH_SIZE": "256",
        },
        clear=True,
    )
    def test_multiple_custom_env_vars(self):
        """Multiple custom env vars should all be reflected."""
        summary = get_batch_config_summary()

        self.assertEqual(summary["OTEL_BSP_MAX_QUEUE_SIZE"]["value"], 8192)
        self.assertTrue(summary["OTEL_BSP_MAX_QUEUE_SIZE"]["customized"])

        self.assertEqual(summary["OTEL_BLRP_MAX_EXPORT_BATCH_SIZE"]["value"], 256)
        self.assertTrue(summary["OTEL_BLRP_MAX_EXPORT_BATCH_SIZE"]["customized"])

        # Others should still be defaults
        self.assertFalse(summary["OTEL_BSP_SCHEDULE_DELAY"]["customized"])

    @patch.dict(os.environ, {"OTEL_BSP_SCHEDULE_DELAY": "not_a_number"}, clear=True)
    def test_invalid_env_var_falls_back_to_default(self):
        """Non-integer env var values should fall back to the default."""
        summary = get_batch_config_summary()
        bsp_delay = summary["OTEL_BSP_SCHEDULE_DELAY"]
        self.assertEqual(bsp_delay["value"], BSP_SCHEDULE_DELAY_MS)
        # Still marked customized because the env var was set (even if invalid)
        self.assertTrue(bsp_delay["customized"])

    @patch.dict(os.environ, {}, clear=True)
    def test_summary_has_all_expected_keys(self):
        """Summary should contain entries for all 8 batch processor env vars."""
        summary = get_batch_config_summary()
        expected_keys = {
            "OTEL_BSP_SCHEDULE_DELAY",
            "OTEL_BSP_MAX_QUEUE_SIZE",
            "OTEL_BSP_MAX_EXPORT_BATCH_SIZE",
            "OTEL_BSP_EXPORT_TIMEOUT",
            "OTEL_BLRP_SCHEDULE_DELAY",
            "OTEL_BLRP_MAX_QUEUE_SIZE",
            "OTEL_BLRP_MAX_EXPORT_BATCH_SIZE",
            "OTEL_BLRP_EXPORT_TIMEOUT",
        }
        self.assertEqual(set(summary.keys()), expected_keys)

    @patch.dict(os.environ, {}, clear=True)
    def test_each_entry_has_required_fields(self):
        """Every entry should have value, default, description, customized."""
        summary = get_batch_config_summary()
        for env_var, entry in summary.items():
            self.assertIn("value", entry, f"{env_var} missing 'value'")
            self.assertIn("default", entry, f"{env_var} missing 'default'")
            self.assertIn("description", entry, f"{env_var} missing 'description'")
            self.assertIn("customized", entry, f"{env_var} missing 'customized'")


class TestLogBatchConfig(unittest.TestCase):
    """Tests for log_batch_config()."""

    @patch.dict(os.environ, {}, clear=True)
    def test_logs_defaults_at_info_level(self):
        """When no env vars are set, should log defaults at INFO."""
        with self.assertLogs("contextcore.compat.otel_batch_config", level="INFO") as cm:
            log_batch_config()

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].levelno, logging.INFO)
        self.assertIn("all defaults", cm.records[0].getMessage())

    @patch.dict(os.environ, {"OTEL_BSP_SCHEDULE_DELAY": "2000"}, clear=True)
    def test_logs_customized_at_info_level(self):
        """When env vars are customized, should log them at INFO."""
        with self.assertLogs("contextcore.compat.otel_batch_config", level="INFO") as cm:
            log_batch_config()

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].levelno, logging.INFO)
        self.assertIn("customized", cm.records[0].getMessage())
        self.assertIn("OTEL_BSP_SCHEDULE_DELAY", cm.records[0].getMessage())


class TestContractsExport(unittest.TestCase):
    """Test that batch processor constants are exported from contracts."""

    def test_constants_importable_from_contracts(self):
        """Batch processor defaults should be importable from contextcore.contracts."""
        from contextcore.contracts import (
            BSP_SCHEDULE_DELAY_MS as c_bsp_delay,
            BSP_MAX_QUEUE_SIZE as c_bsp_queue,
            BSP_MAX_EXPORT_BATCH_SIZE as c_bsp_batch,
            BSP_EXPORT_TIMEOUT_MS as c_bsp_timeout,
            BLRP_SCHEDULE_DELAY_MS as c_blrp_delay,
            BLRP_MAX_QUEUE_SIZE as c_blrp_queue,
            BLRP_MAX_EXPORT_BATCH_SIZE as c_blrp_batch,
            BLRP_EXPORT_TIMEOUT_MS as c_blrp_timeout,
        )

        self.assertEqual(c_bsp_delay, 5000)
        self.assertEqual(c_bsp_queue, 2048)
        self.assertEqual(c_bsp_batch, 512)
        self.assertEqual(c_bsp_timeout, 30000)
        self.assertEqual(c_blrp_delay, 5000)
        self.assertEqual(c_blrp_queue, 2048)
        self.assertEqual(c_blrp_batch, 512)
        self.assertEqual(c_blrp_timeout, 30000)


if __name__ == "__main__":
    unittest.main()
