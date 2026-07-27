// Hybrid MX + Kailh Choc Hotswap Switch Footprint for Ergogen
// Source: pcb/lib/dormin.pretty/SW_MX_Choc_Hotswap.kicad_mod

module.exports = {
  params: {
    designator: 'SW',
    value: 'SW_Push',
    keycaps: false,
    from: undefined,
    to: undefined
  },
  body: p => {
    const val = p.value || 'SW_Push'
    const keycaps = p.keycaps ? `
      (fp_rect (start -9.525 -9.525) (end 9.525 9.525) (stroke (width 0.1) (type solid)) (fill no) (layer "Dwgs.User"))
      (fp_rect (start -7 -7) (end 7 7) (stroke (width 0.1) (type solid)) (fill no) (layer "Dwgs.User"))
    ` : ''

    return `
      (footprint "SW_MX_Choc_Hotswap"
        ${p.at}
        (layer "F.Cu")
        (property "Reference" "${p.ref}" (at 0 -8 0) (layer "F.SilkS") ${p.ref_hide} (effects (font (size 1 1) (thickness 0.15))))
        (property "Value" "${val}" (at 0 8 0) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))

        ${keycaps}

        (pad "" np_thru_hole circle (at 0 0) (size 5.25 5.25) (drill 5.25) (layers "*.Mask"))
        (pad "" np_thru_hole oval (at -5.29 0) (size 2.12 1.7) (drill oval 2.12 1.7) (layers "*.Cu" "*.Mask"))
        (pad "" np_thru_hole oval (at 5.29 0) (size 2.12 1.7) (drill oval 2.12 1.7) (layers "*.Cu" "*.Mask"))
        (pad "" np_thru_hole circle (at -5 3.75) (size 3.05 3.05) (drill 3.05) (layers "*.Cu" "*.Mask"))
        (pad "" np_thru_hole circle (at 0 5.95) (size 3.05 3.05) (drill 3.05) (layers "*.Cu" "*.Mask"))
        (pad "" np_thru_hole circle (at -3.81 -2.54) (size 3.05 3.05) (drill 3.05) (layers "*.Cu" "*.Mask"))
        (pad "" np_thru_hole circle (at 2.54 -5.08) (size 3.05 3.05) (drill 3.05) (layers "*.Cu" "*.Mask"))

        (pad "1" smd roundrect (at -8.245 3.75 ${p.r}) (size 2.65 2.6) (layers "B.Cu" "B.Mask" "B.Paste") (roundrect_rratio 0.1) ${p.from})
        (pad "1" smd roundrect (at -7.36 -2.54 ${p.r}) (size 2.55 2.5) (layers "B.Cu" "B.Mask" "B.Paste") (roundrect_rratio 0.1) ${p.from})

        (pad "2" smd roundrect (at 3.245 5.95 ${p.r}) (size 2.65 2.6) (layers "B.Cu" "B.Mask" "B.Paste") (roundrect_rratio 0.1) ${p.to})
        (pad "2" smd roundrect (at 6.09 -5.08 ${p.r}) (size 2.55 2.5) (layers "B.Cu" "B.Mask" "B.Paste") (roundrect_rratio 0.1) ${p.to})
      )
    `
  }
}
