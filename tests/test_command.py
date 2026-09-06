import json
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
    get_endpoint_save_feed,
    build_save_feed_params,
    build_set_plan_repeats_params,
    get_endpoint_remove_daily_feed,
    get_endpoint_restore_daily_feed,
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

    def test_get_endpoint_save_feed_snake_case_for_mini_and_legacy_feeder(self):
        mini = type(
            "Device",
            (object,),
            {
                "device_nfo": type(
                    "DeviceInfo", (object,), {"device_type": FEEDER_MINI}
                )()
            },
        )
        self.assertEqual(get_endpoint_save_feed(mini), PetkitEndpoint.SAVE_FEED_OLD)
        legacy = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(get_endpoint_save_feed(legacy), PetkitEndpoint.SAVE_FEED_OLD)
        d3 = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D3})()},
        )
        self.assertEqual(get_endpoint_save_feed(d3), PetkitEndpoint.SAVE_FEED)

    def test_build_save_feed_legacy_feedermini_uses_items_and_repeats(self):
        """Legacy families post a flat items list, not feedDailyList."""
        device = type(
            "Device",
            (),
            {
                "id": 999,
                "device_nfo": type("Info", (), {"device_type": FEEDER_MINI})(),
            },
        )()
        api_days = [
            {
                "count": 2,
                "items": [
                    {
                        "amount": 15,
                        "amount1": 0,
                        "amount2": 0,
                        "deviceId": 0,
                        "deviceType": 0,
                        "id": 18000,
                        "name": "A",
                        "petAmount": [],
                        "time": 18000,
                    },
                    {
                        "amount": 25,
                        "amount1": 0,
                        "amount2": 0,
                        "deviceId": 0,
                        "deviceType": 0,
                        "id": 72000,
                        "name": "B",
                        "petAmount": [],
                        "time": 72000,
                    },
                ],
                "repeats": "1",
                "suspended": 0,
                "totalAmount": 40,
                "totalAmount1": 0,
                "totalAmount2": 0,
            },
            {
                "count": 2,
                "items": [
                    {
                        "amount": 15,
                        "amount1": 0,
                        "amount2": 0,
                        "deviceId": 0,
                        "deviceType": 0,
                        "id": 18000,
                        "name": "A",
                        "petAmount": [],
                        "time": 18000,
                    },
                    {
                        "amount": 25,
                        "amount1": 0,
                        "amount2": 0,
                        "deviceId": 0,
                        "deviceType": 0,
                        "id": 72000,
                        "name": "B",
                        "petAmount": [],
                        "time": 72000,
                    },
                ],
                "repeats": "3",
                "suspended": 0,
                "totalAmount": 40,
                "totalAmount1": 0,
                "totalAmount2": 0,
            },
        ]
        params = build_save_feed_params(device, api_days)
        self.assertNotIn("feedDailyList", params)
        self.assertEqual(params["deviceId"], "999")
        self.assertEqual(params["repeats"], "1,3")
        items = json.loads(params["items"])
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["amount"], 15)
        self.assertEqual(items[0]["deviceId"], 999)
        self.assertEqual(items[0]["deviceType"], 6)
        self.assertEqual(items[1]["name"], "B")

    def _mini(self, device_id=42):
        return type(
            "Device",
            (),
            {
                "id": device_id,
                "device_nfo": type("Info", (), {"device_type": FEEDER_MINI})(),
            },
        )()

    @staticmethod
    def _shape_a_week(items, mask, suspended=0):
        """The 7-day list the HA layer hands us: out-of-mask days carry no repeats."""
        return [
            {
                "repeats": str(oem) if oem in mask else "",
                "suspended": suspended,
                "count": len(items) if oem in mask else 0,
                "items": [dict(it) for it in items] if oem in mask else [],
            }
            for oem in range(1, 8)
        ]

    def test_build_save_feed_legacy_empty_items_matches_app_clear(self):
        """The app's plan editor still POSTs save_feed after removing every slot."""
        params = build_save_feed_params(self._mini(), [])
        self.assertEqual(json.loads(params["items"]), [])
        self.assertEqual(params["repeats"], "1,2,3,4,5,6,7")

    def test_build_save_feed_legacy_clearing_meals_keeps_the_mask(self):
        """The shared-plan editor posts items=[] with ``repeats`` untouched."""
        params = build_save_feed_params(self._mini(), self._shape_a_week([], {2, 4, 6}))
        self.assertEqual(json.loads(params["items"]), [])
        self.assertEqual(params["repeats"], "2,4,6")

    def test_build_save_feed_legacy_week_collapses_without_widening_mask(self):
        """A Mon/Wed/Fri plan must not come back as every day."""
        item = {"time": 28800, "name": "A", "amount": 10, "id": 100001}
        params = build_save_feed_params(
            self._mini(), self._shape_a_week([item], {2, 4, 6})
        )
        self.assertEqual(params["repeats"], "2,4,6")
        items = json.loads(params["items"])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["time"], 28800)

    def test_build_save_feed_legacy_sends_suspended(self):
        """The app's plan save posts deviceId+items+repeats+suspended."""
        item = {"time": 28800, "name": "A", "amount": 10, "id": 100001}
        params = build_save_feed_params(
            self._mini(), self._shape_a_week([item], {2, 4, 6}, suspended=1)
        )
        self.assertEqual(params["suspended"], "1")
        self.assertEqual(params["repeats"], "2,4,6")

    def test_build_save_feed_coerces_unset_amounts(self):
        """Cloud models leave the unused hopper fields None."""
        item = {
            "time": 28800,
            "name": "A",
            "amount": 10,
            "amount1": None,
            "amount2": None,
            "id": 100001,
        }
        params = build_save_feed_params(self._mini(), self._shape_a_week([item], {2}))
        sent = json.loads(params["items"])[0]
        self.assertEqual(sent["amount1"], 0)
        self.assertEqual(sent["amount2"], 0)

    def test_build_save_feed_d3_items_carry_device_identity(self):
        """The per-day editor sets the real id and family type_id."""
        device = type(
            "Device",
            (),
            {"id": 777, "device_nfo": type("Info", (), {"device_type": D3})()},
        )()
        days = [
            {
                "repeats": str(oem),
                "suspended": 0,
                "count": 1 if oem == 2 else 0,
                "items": (
                    [
                        {
                            "time": 28800,
                            "name": "B",
                            "amount": 30,
                            "amount1": None,
                            "id": 0,
                            "petAmount": [{"petId": "p1", "amount": 30}],
                        }
                    ]
                    if oem == 2
                    else []
                ),
            }
            for oem in range(1, 8)
        ]
        sent = json.loads(build_save_feed_params(device, days)["feedDailyList"])
        item = sent[1]["items"][0]
        self.assertEqual(item["deviceId"], 777)
        self.assertEqual(item["deviceType"], 9)
        # id 0 is rewritten from time, as the per-day editor does.
        self.assertEqual(item["id"], 28800)
        self.assertEqual(item["petAmount"], [{"petId": "p1", "amount": 30}])
        self.assertEqual(item["amount1"], 0)

    def test_build_save_feed_d3_uses_feed_daily_list_json(self):
        device = type(
            "Device",
            (),
            {"id": 1, "device_nfo": type("Info", (), {"device_type": D3})()},
        )()
        blob = [{"count": 0, "items": [], "repeats": "1", "suspended": 0}]
        params = build_save_feed_params(device, blob)
        self.assertIn("feedDailyList", params)
        self.assertEqual(json.loads(params["feedDailyList"]), blob)

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

    def test_actions_map_remove_restore_daily_feed(self):
        """Skip-today commands stay registered with snake/camel endpoint callables."""
        self.assertIn(FeederCommand.REMOVE_DAILY_FEED, ACTIONS_MAP)
        self.assertIs(
            ACTIONS_MAP[FeederCommand.REMOVE_DAILY_FEED].endpoint,
            get_endpoint_remove_daily_feed,
        )
        self.assertIn(FeederCommand.RESTORE_DAILY_FEED, ACTIONS_MAP)
        self.assertIs(
            ACTIONS_MAP[FeederCommand.RESTORE_DAILY_FEED].endpoint,
            get_endpoint_restore_daily_feed,
        )

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

    def test_remove_daily_feed_endpoint_old_feeder(self):
        """D1/D2 skip-today uses snake_case remove_dailyfeed."""
        mini = type(
            "Device",
            (object,),
            {
                "device_nfo": type(
                    "DeviceInfo", (object,), {"device_type": FEEDER_MINI}
                )()
            },
        )
        self.assertEqual(
            get_endpoint_remove_daily_feed(mini),
            PetkitEndpoint.REMOVE_DAILY_FEED_OLD,
        )
        d3 = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D3})()},
        )
        self.assertEqual(
            get_endpoint_remove_daily_feed(d3),
            PetkitEndpoint.REMOVE_DAILY_FEED,
        )

    def test_restore_daily_feed_endpoint_old_feeder(self):
        """D1/D2 skip-today uses snake_case restore_dailyfeed."""
        feeder = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": FEEDER})()},
        )
        self.assertEqual(
            get_endpoint_restore_daily_feed(feeder),
            PetkitEndpoint.RESTORE_DAILY_FEED_OLD,
        )
        d4h = type(
            "Device",
            (object,),
            {"device_nfo": type("DeviceInfo", (object,), {"device_type": D4H})()},
        )
        self.assertEqual(
            get_endpoint_restore_daily_feed(d4h),
            PetkitEndpoint.RESTORE_DAILY_FEED,
        )


if __name__ == "__main__":
    unittest.main()


class TestSetPlanRepeats(unittest.TestCase):
    """The D1/Mini plan-level Repeat control, saved the way the app saves it."""

    class _Item:
        """Attribute bag, like the pydantic FeedItem the client attaches."""

        def __init__(self, **kw):
            self.__dict__.update(kw)

    def _device(self, device_type=FEEDER_MINI, repeats="2,4,6", suspended=0):
        item = self._Item(
            time=28800,
            name="Breakfast",
            amount=60,
            amount1=None,
            amount2=None,
            id=100001,
            pet_amount=None,
        )
        return type(
            "Device",
            (),
            {
                "id": 999,
                "device_nfo": type("Info", (), {"device_type": device_type})(),
                "feed_plan": type(
                    "Plan",
                    (),
                    {"items": [item], "repeats": repeats, "suspended": suspended},
                )(),
            },
        )()

    def test_saves_through_save_feed_not_save_repeats(self):
        """The app (13.9.2) never calls save_repeats, so neither do we."""
        params = build_set_plan_repeats_params(self._device(), {"repeats": "2,3,4,5,6"})
        self.assertEqual(params["repeats"], "2,3,4,5,6")
        self.assertEqual(params["deviceId"], "999")
        self.assertIn("items", params)
        self.assertIn("suspended", params)

    def test_keeps_the_existing_meals(self):
        params = build_set_plan_repeats_params(self._device(), "1,7")
        items = json.loads(params["items"])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["time"], 28800)
        self.assertEqual(items[0]["amount"], 60)
        self.assertEqual(items[0]["id"], 100001)
        self.assertEqual(items[0]["deviceType"], 6)

    def test_sorts_and_deduplicates_the_mask(self):
        params = build_set_plan_repeats_params(self._device(), "7,2,2,4")
        self.assertEqual(params["repeats"], "2,4,7")

    def test_preserves_a_paused_plan(self):
        params = build_set_plan_repeats_params(
            self._device(suspended=1), {"repeats": "3"}
        )
        self.assertEqual(params["suspended"], "1")

    def test_rejects_an_empty_mask(self):
        """The app refuses an empty mask rather than saving one."""
        for bad in ("", "0", "8,9", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    build_set_plan_repeats_params(self._device(), {"repeats": bad})

    def test_rejects_a_device_with_no_plan_loaded(self):
        device = type(
            "Device",
            (),
            {
                "id": 999,
                "device_nfo": type("Info", (), {"device_type": FEEDER_MINI})(),
                "feed_plan": None,
            },
        )()
        with self.assertRaises(ValueError):
            build_set_plan_repeats_params(device, {"repeats": "2"})
