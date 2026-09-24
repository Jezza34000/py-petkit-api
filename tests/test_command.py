import unittest
from pypetkitapi.command import (
    DeviceCommand,
    FountainCommand,
    FeederCommand,
    LitterCommand,
    PetCommand,
    LBCommand,
    PurMode,
    DeviceAction,
    FountainAction,
    FOUNTAIN_COMMAND,
    CmdData,
    get_endpoint_manual_feed,
    get_endpoint_reset_desiccant,
    get_endpoint_suspend_feed,
    get_endpoint_restore_feed,
    get_endpoint_save_repeats,
    build_cancel_manual_feed_params,
    ACTIONS_MAP,
)
from pypetkitapi.const import (
    PetkitEndpoint,
    FEEDER_MINI,
    FEEDER,
    D3,
    D4H,
    D4S,
    D4SH,
    W7H,
)
from pypetkitapi.feeder_container import ManualFeed


class TestCommandModule(unittest.TestCase):

    def test_device_command(self):
        self.assertEqual(DeviceCommand.POWER, "power_device")
        self.assertEqual(DeviceCommand.CONTROL_DEVICE, "control_device")
        self.assertEqual(DeviceCommand.UPDATE_SETTING, "update_setting")

    def test_fountain_command(self):
        self.assertEqual(FountainCommand.CONTROL_DEVICE, "control_device")

    def test_feeder_command(self):
        self.assertEqual(FeederCommand.CALL_PET, "call_pet")
        self.assertEqual(FeederCommand.CALIBRATION, "food_reset")
        self.assertEqual(FeederCommand.MANUAL_FEED, "manual_feed")

    def test_litter_command(self):
        self.assertEqual(LitterCommand.RESET_N50_DEODORIZER, "reset_deodorizer")

    def test_pet_command(self):
        self.assertEqual(PetCommand.UPDATE_USAGE_RECORD, "update_usage_record")
        self.assertEqual(PetCommand.PET_UPDATE_SETTING, "pet_update_setting")

    def test_lb_command(self):
        self.assertEqual(LBCommand.CLEANING, 0)
        self.assertEqual(LBCommand.DUMPING, 1)

    def test_pur_mode(self):
        self.assertEqual(PurMode.AUTO_MODE, 0)
        self.assertEqual(PurMode.SILENT_MODE, 1)

    def test_device_action(self):
        self.assertEqual(DeviceAction.CONTINUE, "continue_action")
        self.assertEqual(DeviceAction.END, "end_action")

    def test_fountain_action(self):
        self.assertEqual(FountainAction.MODE_NORMAL, "Normal")
        self.assertEqual(FountainAction.PAUSE, "Pause")

    def test_fountain_command_mapping(self):
        self.assertIn(FountainAction.PAUSE, FOUNTAIN_COMMAND)
        self.assertEqual(
            FOUNTAIN_COMMAND[FountainAction.PAUSE], [220, 1, 3, 0, 1, 0, 2]
        )

    def test_get_endpoint_manual_feed(self):
        device = type(
            "Device",
            (object,),
            {
                "device_nfo": type(
                    "DeviceInfo", (object,), {"device_type": FEEDER_MINI}
                )()
            },
        )
        self.assertEqual(
            get_endpoint_manual_feed(device), PetkitEndpoint.MANUAL_FEED_OLD
        )

    def test_get_endpoint_reset_desiccant(self):
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(
            get_endpoint_reset_desiccant(device),
            PetkitEndpoint.DESICCANT_RESET_OLD,
        )

    def test_build_cancel_manual_feed_params(self):
        """Test the manual feed id is sent only where it exists and is used."""
        cases = [
            # device_type, manual_feed, expected "id" in the params
            (FEEDER, ManualFeed(id="feed-1"), None),
            (FEEDER_MINI, ManualFeed(id="feed-1"), None),
            (D3, ManualFeed(id="feed-1"), None),
            (D4H, ManualFeed(id="feed-1"), "feed-1"),
            (D4S, ManualFeed(id="feed-2"), "feed-2"),
            (D4SH, ManualFeed(id="feed-3"), "feed-3"),
            (D4H, ManualFeed(id=None), None),
            (D4H, None, None),
        ]
        for device_type, manual_feed, expected_id in cases:
            with self.subTest(device_type=device_type, manual_feed=manual_feed):
                device = type(
                    "Device",
                    (object,),
                    {
                        "device_nfo": type(
                            "DeviceInfo", (object,), {"device_type": device_type}
                        )(),
                        "id": 10197308,
                        "manual_feed": manual_feed,
                    },
                )
                params = build_cancel_manual_feed_params(device)
                self.assertEqual(params["deviceId"], 10197308)
                self.assertIn("day", params)
                self.assertEqual(params.get("id"), expected_id)

    def test_actions_map_cancel_manual_feed_uses_builder(self):
        """Test CANCEL_MANUAL_FEED is wired to the params builder."""
        self.assertIn(FeederCommand.CANCEL_MANUAL_FEED, ACTIONS_MAP)
        self.assertIs(
            ACTIONS_MAP[FeederCommand.CANCEL_MANUAL_FEED].params,
            build_cancel_manual_feed_params,
        )

    def test_actions_map(self):
        self.assertIn(DeviceCommand.UPDATE_SETTING, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[DeviceCommand.UPDATE_SETTING], CmdData)

    def test_actions_map_control_device_supports_w7h(self):
        """Test that CONTROL_DEVICE supports W7H fountain device."""
        self.assertIn(DeviceCommand.CONTROL_DEVICE, ACTIONS_MAP)
        supported = ACTIONS_MAP[DeviceCommand.CONTROL_DEVICE].supported_device
        self.assertIn(W7H, supported)

    def test_feeder_command_save_feed(self):
        """Test that SAVE_FEED is defined in FeederCommand."""
        self.assertEqual(FeederCommand.SAVE_FEED, "save_feed")

    def test_actions_map_save_feed(self):
        """Test that SAVE_FEED is registered in ACTIONS_MAP."""
        self.assertIn(FeederCommand.SAVE_FEED, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[FeederCommand.SAVE_FEED], CmdData)

    def test_feeder_command_suspend_feed(self):
        """Test that SUSPEND_FEED is defined in FeederCommand."""
        self.assertEqual(FeederCommand.SUSPEND_FEED, "suspend_feed")

    def test_feeder_command_restore_feed(self):
        """Test that RESTORE_FEED is defined in FeederCommand."""
        self.assertEqual(FeederCommand.RESTORE_FEED, "restore_feed")

    def test_feeder_command_save_repeats(self):
        """Test that SAVE_REPEATS is defined in FeederCommand."""
        self.assertEqual(FeederCommand.SAVE_REPEATS, "save_repeats")

    def test_actions_map_suspend_feed(self):
        """Test that SUSPEND_FEED is registered in ACTIONS_MAP."""
        self.assertIn(FeederCommand.SUSPEND_FEED, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[FeederCommand.SUSPEND_FEED], CmdData)

    def test_actions_map_restore_feed(self):
        """Test that RESTORE_FEED is registered in ACTIONS_MAP."""
        self.assertIn(FeederCommand.RESTORE_FEED, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[FeederCommand.RESTORE_FEED], CmdData)

    def test_actions_map_save_repeats(self):
        """Test that SAVE_REPEATS is registered in ACTIONS_MAP."""
        self.assertIn(FeederCommand.SAVE_REPEATS, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[FeederCommand.SAVE_REPEATS], CmdData)

    def test_suspend_feed_endpoint_old_feeder(self):
        """Test suspend feed returns old endpoint for Feeder."""
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(
            get_endpoint_suspend_feed(device),
            PetkitEndpoint.SUSPEND_FEED_OLD,
        )

    def test_suspend_feed_endpoint_new_feeder(self):
        """Test suspend feed returns new endpoint for D4H."""
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D4H})()},
        )
        self.assertEqual(
            get_endpoint_suspend_feed(device),
            PetkitEndpoint.SUSPEND_FEED_NEW,
        )

    def test_restore_feed_endpoint_old_feeder(self):
        """Test restore feed returns old endpoint for Feeder."""
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(
            get_endpoint_restore_feed(device),
            PetkitEndpoint.RESTORE_FEED_OLD,
        )

    def test_restore_feed_endpoint_new_feeder(self):
        """Test restore feed returns new endpoint for D3."""
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D3})()},
        )
        self.assertEqual(
            get_endpoint_restore_feed(device),
            PetkitEndpoint.RESTORE_FEED_NEW,
        )

    def test_save_repeats_endpoint_old_feeder(self):
        """Test save repeats returns old endpoint for FeederMini."""
        device = type(
            "Device",
            (object,),
            {
                "device_nfo": type(
                    "DeviceInfo", (object,), {"device_type": FEEDER_MINI}
                )()
            },
        )
        self.assertEqual(
            get_endpoint_save_repeats(device),
            PetkitEndpoint.SAVE_REPEATS_OLD,
        )

    def test_save_repeats_endpoint_new_feeder(self):
        """Test save repeats returns new endpoint for D4H."""
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D4H})()},
        )
        self.assertEqual(
            get_endpoint_save_repeats(device),
            PetkitEndpoint.SAVE_REPEATS_NEW,
        )


if __name__ == "__main__":
    unittest.main()
