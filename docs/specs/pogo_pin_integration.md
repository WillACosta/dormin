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
````
