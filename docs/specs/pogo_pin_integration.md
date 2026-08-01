```mermaid
flowchart LR
    subgraph Left["Main / Left Keyboard Half - Schema v2 (Diode Added)"]
        L_XIAO["XIAO nRF52840"]
        L_BAT("LiPo Battery")
        L_DIODE["Schottky Diode (e.g. B5819WS)"]
        L_POGO["4-Pin Pogo Connector"]
        L_R1["330Ω Resistor"]
        L_R2["330Ω Resistor"]

        L_XIAO ---|BAT+| L_BAT
        L_XIAO ---|5V / VBUS| L_DIODE
        L_DIODE ---|Cathode → Pin 1| L_POGO
        L_XIAO ---|GND → Pin 2| L_POGO

        L_XIAO ---|GPIO TX| L_R1
        L_R1 ---|Pin 3| L_POGO

        L_XIAO ---|GPIO RX| L_R2
        L_R2 ---|Pin 4| L_POGO
    end

    subgraph Right["Peripheral / Right Keyboard Half"]
        R_POGO["4-Pad Target Contact"]
        R_XIAO["XIAO nRF52840"]
        R_BAT("LiPo Battery")
        R_R1["330Ω Resistor"]
        R_R2["330Ω Resistor"]

        R_POGO ---|Pad 1 → 5V / VBUS| R_XIAO
        R_POGO ---|Pad 2 → GND| R_XIAO

        R_POGO ---|Pad 3| R_R1
        R_R1 ---|GPIO TX| R_XIAO

        R_POGO ---|Pad 4| R_R2
        R_R2 ---|GPIO RX| R_XIAO

        R_XIAO ---|BAT+| R_BAT
    end

    L_POGO ===|Physical Magnetic Mating| R_POGO
```

```mermaid
flowchart LR

%% =====================================================================
%% LEFT HALF
%% =====================================================================

subgraph LEFT["Main / Left Half"]

    USB["USB_VBUS"]
    PF["Polyfuse (Optional)"]
    D["Schottky Diode"]
    TVS5L["5V TVS"]

    MCU_L["XIAO nRF52840 Plus"]
    BAT_L["LiPo Battery"]

    TVSD_L["2-Channel TVS"]
    R1["33Ω"]
    R2["33Ω"]

    POGO_L["4-Pin Pogo Connector"]

    BAT_L <-->|BAT+/BAT-| MCU_L

    USB --> PF
    PF --> D
    D --> POGO_L

    POGO_L --- TVS5L
    TVS5L --> GNDL["GND"]

    MCU_L --> R1
    R1 --> TVSD_L
    TVSD_L --> POGO_L

    MCU_L --> R2
    R2 --> TVSD_L

    MCU_L --- GNDL
    GNDL --> POGO_L

end

%% =====================================================================
%% RIGHT HALF
%% =====================================================================

subgraph RIGHT["Peripheral / Right Half"]

    POGO_R["4-Pin Target Pads"]

    TVS5R["5V TVS"]
    TVSD_R["2-Channel TVS"]

    R3["33Ω"]
    R4["33Ω"]

    MCU_R["XIAO nRF52840 Plus"]
    BAT_R["LiPo Battery"]

    GNDR["GND"]

    BAT_R <-->|BAT+/BAT-| MCU_R

    POGO_R --> MCU_R

    POGO_R --- TVS5R
    TVS5R --> GNDR

    POGO_R --> TVSD_R
    TVSD_R --> R3
    R3 --> MCU_R

    TVSD_R --> R4
    R4 --> MCU_R

    POGO_R --> GNDR
    MCU_R --- GNDR

end

%% =====================================================================
%% MECHANICAL CONNECTION
%% =====================================================================

POGO_L ===|"Magnetic Pogo Interface"| POGO_R
```

## BOM

| Function                              | Recommended Part                                                       | Package                                       | KiCad Footprint                              | Placement Rule                                                      | Routing Rule                                                                                                                | Notes                                                                                           |
| ------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **Magnetic Pogo Connector**           | Xinyangze **YZP0048-20048-04025-03** _(or equivalent 4-pin connector)_ | Vendor-specific                               | **Custom footprint**                         | **On the PCB edge**, aligned with the enclosure and magnets.        | Keep `POGO_VBUS`, `POGO_GND`, `POGO_LINK_IO1`, and `POGO_LINK_IO2` as short as practical leaving the connector.             | Verify mechanical clearance using the STEP model before manufacturing.                          |
| **Reverse Current Protection**        | **B5819WS**                                                            | SOD-323 / SOD-123W _(manufacturer dependent)_ | `Diode_SMD:D_SOD-323` or matching package    | **Near the USB/XIAO power input**, **not** near the pogo connector. | Route `USB_VBUS → Polyfuse → Schottky → POGO_VBUS`.                                                                         | Prevents power from the pogo connector or battery from backfeeding into the USB supply.         |
| **Overcurrent Protection (Optional)** | Polyfuse ~500 mA Hold _(e.g. 0ZCJ0050AF2E)_                            | 1206                                          | `Fuse:Fuse_1206_3216Metric`                  | Immediately after the USB power source.                             | Place before the Schottky diode.                                                                                            | Optional, but recommended for a premium design to protect against shorts on the pogo interface. |
| **VBUS ESD Protection**               | **SMF5.0A**                                                            | DO-219AB (SMF)                                | `Diode_SMD:D_SMF`                            | **As close as possible to the pogo connector.**                     | Connect **directly between `POGO_VBUS` and `GND`**. Use a **very short trace** and **dedicated GND via** beside the device. | First line of defense against ESD and transient surges on the charging pin.                     |
| **GPIO ESD Protection**               | **TPD2E2U06DCKR**                                                      | SC70-3 (DCK)                                  | `Package_TO_SOT_SMD:SOT-353_SC-70-3`         | **Immediately beside the pogo connector.**                          | Signal flow should be: **Pogo → TVS → 33 Ω → MCU**. Connect GND with a **dedicated via** next to the GND pin.               | Protects the exposed communication lines (`POGO_LINK_IO1`, `POGO_LINK_IO2`) from ESD.           |
| **Series Resistors**                  | **33 Ω ±1%**                                                           | 0402 or 0603                                  | `Resistor_SMD:R_0402_1005Metric` _(or 0603)_ | **Near the MCU**, not the connector.                                | One resistor per communication line, placed **after the TVS** and **before the MCU GPIO**.                                  | Improves signal integrity and limits transient current into the MCU.                            |
