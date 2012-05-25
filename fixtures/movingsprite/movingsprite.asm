; Just a small test with palettes, sprites and controllers
; Assemble with NESASM. ASM6 will work if you change some stuff

; iNES header
  .inesprg 1
  .ineschr 1
  .inesmap 0
  .inesmir 1

; First bank
  .bank 0
  .org $C000

WAITVBLANK:
  BIT $2002
  BPL WAITVBLANK
  RTS

RESET:
  SEI          ; no IRQs (no mappers)
  CLD          ; no decimal mode in NES
  LDX #$40
  STX $4017
  LDX #$FF
  TXS
  INX
  STX $2000
  STX $2001
  STX $4010
  
  JSR WAITVBLANK

CLEARMEM:
  LDA #$00
  STA $0000, x
  STA $0100, x
  STA $0200, x
  STA $0400, x
  STA $0500, x
  STA $0600, x
  STA $0700, x
  LDA #$FE
  STA $0300, x
  INX
  BNE CLEARMEM
  
  JSR WAITVBLANK

; Palette loading

LoadPalettes:
  LDA $2002             ; Reset PPU, start writing
  LDA #$3F
  STA $2006             ; High byte = $3F00
  LDA #$00
  STA $2006             ; Low byte = $3F00
  LDX #$00
LoadPalettesIntoPPU:
  LDA palette, x
  STA $2007
  INX
  CPX #$20                  ; Hex 20 = 32 decimal
  BNE LoadPalettesIntoPPU

LoadSprites:
  LDX #$00
LoadSpritesIntoPPU:
  LDA sprites, x
  STA $0200, x
  INX
  CPX #$20                  ; Hex 20 = 32 decimal
  BNE LoadSpritesIntoPPU

  LDA #%10000000
  STA $2000
  LDA #%00010000
  STA $2001

InfiniteLoop:
  JMP InfiniteLoop

NMI:
  LDA #$00
  STA $2003
  LDA #$02
  STA $4014

; Read controllers and reset positions
StartInput:
  LDA #$01
  STA $4016
  LDA #$00
  STA $4016

; Reading A button
StartA: 
  LDA $4016
  AND #%00000001
  BEQ EndA
EndA:

; Reading B button
StartB: 
  LDA $4016
  AND #%00000001
  BEQ EndB
EndB:

; Reading Select button
StartSelect: 
  LDA $4016
  AND #%00000001
  BEQ EndSelect
EndSelect:

; Reading Start button
StartStart: 
  LDA $4016
  AND #%00000001
  BEQ EndStart
EndStart:

; Reading Up button
StartUp: 
  LDA $4016
  AND #%00000001
  BEQ EndUp
  LDA $0200       ; Y position
  SEC
  SBC #$01        ; Y = Y - 1
  STA $0200
EndUp:

; Reading Down button
StartDown: 
  LDA $4016
  AND #%00000001
  BEQ EndDown
  LDA $0200       ; Y position
  CLC
  ADC #$01        ; Y = Y + 1
  STA $0200
EndDown:

; Reading Left button
StartLeft: 
  LDA $4016
  AND #%00000001
  BEQ EndLeft
  LDA $0203       ; X Position
  SEC
  SBC #$01        ; X = X - 1
  STA $0203
EndLeft:

; Reading Right button
StartRight: 
  LDA $4016
  AND #%00000001
  BEQ EndRight
  LDA $0203       ; X Position
  CLC
  ADC #$01        ; X = X + 1
  STA $0203
EndRight:
  
  RTI             ; NMI return

; Second bank
  .bank 1
  .org $E000

palette:
  .db $0F,$01,$02,$03,$04,$05,$06,$07,$08,$09,$0A,$0B,$0C,$0D,$0E,$0F
  .db $0F,$30,$31,$32,$33,$35,$36,$37,$38,$39,$3A,$3B,$3C,$3D,$3E,$0F

sprites:
  .db $80, $00, $03, $80; Y pos, tile id, attributes, X pos

  .org $FFFA
  .dw NMI
  .dw RESET
  .dw 0

; Third bank
  .bank 2
  .org $0000
  .incbin "player.chr"
