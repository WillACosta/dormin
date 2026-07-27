# Ergogen Layout Configuration

Ergogen is used to generate key switch positions, panel outlines, and KiCad PCB drafts.

## Generating Ergogen Files

To generate the PCB layout (`.kicad_pcb`) and outline assets using Ergogen:

1. **Run Ergogen CLI**:
   ```bash
   npx ergogen keyboard/ergogen -o keyboard/generated
   ```

2. **Generated Output (`keyboard/generated/`)**:
   - `keyboard/generated/pcbs/dormin.kicad_pcb`: Contains the KiCad PCB with switch footprints (`SW1` to `SW42`) using standard MX spacing and Edge.Cuts outlines.
   - `keyboard/generated/outlines/`: Contains DXF/SVG outline assets for switch plates and case panels.
