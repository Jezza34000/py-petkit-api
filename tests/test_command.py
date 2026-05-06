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
    ACTIONS_MAP,
)
from pypetkitapi.const import PetkitEndpoint, FEEDER_MINI, FEEDER, D3, D4H


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

    def test_actions_map(self):
        self.assertIn(DeviceCommand.UPDATE_SETTING, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[DeviceCommand.UPDATE_SETTING], CmdData)

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
