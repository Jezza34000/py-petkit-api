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
    ACTIONS_MAP,
)
from pypetkitapi.const import PetkitEndpoint, FEEDER_MINI, FEEDER


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
        self.assertEqual(LitterCommand.RESET_DEODORIZER, "reset_deodorizer")

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
            get_endpoint_manual_feed(device), PetkitEndpoint.MANUAL_FEED_MINI
        )

    def test_get_endpoint_reset_desiccant(self):
        device = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(
            get_endpoint_reset_desiccant(device),
            PetkitEndpoint.FRESH_ELEMENT_DESICCANT_RESET,
        )

    def test_actions_map(self):
        self.assertIn(DeviceCommand.UPDATE_SETTING, ACTIONS_MAP)
        self.assertIsInstance(ACTIONS_MAP[DeviceCommand.UPDATE_SETTING], CmdData)


if __name__ == "__main__":
    unittest.main()
