# V8.9 Adaptive Multi-point Branch Validation

- Adaptive groups: **20**
- Explicit ordered rules: **137**
- Synthetic branch scenarios: **4118**
- Errors: **0**
- Warnings: **0**

## Covered groups
- TM_PRESSURE_TAPS: 8 rules
- HYD_MAIN_RELIEF: 5 rules
- START_VDROP: 7 rules
- OSS_HEALTH: 6 rules
- ENG_ECU_HEALTH: 6 rules
- ENG_VREF: 6 rules
- ENG_CRANK_START: 8 rules
- ENG_FUEL_RAIL: 8 rules
- ENG_SYNC: 6 rules
- ENG_INJECTOR: 8 rules
- ENG_AIR_BOOST: 8 rules
- ENG_COOLING: 8 rules
- ENG_LUBE: 7 rules
- ENG_PREHEAT: 7 rules
- ENG_COMBUSTION: 8 rules
- EL_STOP_LAMP: 7 rules
- EL_CHARGE: 5 rules
- EL_FR_CONTROL: 7 rules
- EL_AC_POWER: 7 rules
- EL_CAN_NETWORK: 5 rules

## Guardrails
- A matched rule narrows a circuit/system; it does not automatically authorize part replacement.
- No new voltage/pressure threshold is created by the adaptive engine.
- Rule conditions only consume PASS/FAIL/HOLD states already recorded by the worksheet or OEM-exact auto evaluator.
