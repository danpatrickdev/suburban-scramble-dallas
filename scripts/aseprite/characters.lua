-- Suburban Scramble: Dallas Edition — sprite + portrait + enemy generator
-- Run from project root with:
--   /Applications/Aseprite.app/Contents/MacOS/aseprite -b --script scripts/aseprite/characters.lua
--
-- Writes:
--   static/assets/characters/<id>.png + .json + .aseprite     (32x32 top-down, 14 frames)
--   static/assets/ui/portraits/<id>.png                        (96x96 native front-facing)
--   static/assets/enemies/<id>.png + .json + .aseprite         (top-down enemies)
--   static/assets/bosses/main_character.png + .json + .aseprite
--   static/assets/tiles/katy_trail.png                         (64x64)
--
-- All sprite sheets use {tag}_{tagframe} filename format so Phaser anim keys
-- are `idle_0..3 / walk_0..3 / attack_0..2 / special_0..2`.

local OUT_CHARS = "static/assets/characters"
local OUT_PORTRAITS = "static/assets/ui/portraits"
local OUT_ENEMIES = "static/assets/enemies"
local OUT_BOSSES = "static/assets/bosses"
local OUT_TILES = "static/assets/tiles"
local SPRITE = 32
local PORTRAIT = 96

local function rgb(r, g, b, a) return Color{ r=r, g=g, b=b, a=(a or 255) } end

-- ============================================================================
-- Palettes
-- ============================================================================
local PAL = {
    rosie = {
        black     = rgb(20, 20, 24),
        black_h   = rgb(48, 48, 56),    -- highlight on black fur
        white     = rgb(245, 245, 240),
        white_s   = rgb(200, 200, 195), -- shadow on white fur
        amber     = rgb(255, 176, 0),   -- iconic BC eye color
        amber_h   = rgb(255, 220, 120),
        pink      = rgb(225, 130, 145), -- tongue / inner ear
        nose      = rgb(28, 24, 28)
    },
    charlie = {
        black     = rgb(22, 22, 26),
        black_h   = rgb(50, 48, 56),
        white     = rgb(245, 245, 240),
        white_s   = rgb(200, 200, 195),
        tan       = rgb(155, 100, 45),   -- darker brown patches
        tan_h     = rgb(195, 140, 75),   -- kabuki brow tan
        tan_l     = rgb(225, 175, 100),
        amber     = rgb(184, 124, 60),   -- charlie has darker eyes
        pink      = rgb(225, 130, 145),
        nose      = rgb(28, 24, 28)
    },
    katie = {
        skin      = rgb(241, 199, 165),
        skin_s    = rgb(208, 156, 122),
        skin_h    = rgb(255, 222, 196),
        hair      = rgb(72, 44, 30),
        hair_h    = rgb(110, 76, 52),
        pink      = rgb(248, 182, 203),
        pink_d    = rgb(220, 138, 165),
        pink_h    = rgb(255, 210, 224),
        black     = rgb(28, 28, 32),
        watch_face= rgb(255, 215, 0),
        watch_band= rgb(60, 60, 64),
        white     = rgb(245, 245, 240),
        eye       = rgb(80, 50, 30),     -- brown
        lip       = rgb(200, 100, 110)
    },
    tia = {
        grey      = rgb(140, 143, 149),
        grey_d    = rgb(98, 100, 108),
        grey_h    = rgb(180, 183, 190),
        white     = rgb(245, 245, 240),
        white_s   = rgb(195, 195, 190),
        green     = rgb(98, 168, 92),
        green_h   = rgb(160, 220, 130),
        pink      = rgb(220, 130, 150),
        black     = rgb(20, 20, 24),
        stripe    = rgb(78, 80, 88)
    },
    nancy = {
        grey      = rgb(166, 168, 172),
        grey_d    = rgb(118, 120, 128),
        grey_h    = rgb(195, 197, 202),
        white     = rgb(245, 245, 240),
        white_s   = rgb(195, 195, 190),
        green     = rgb(98, 168, 92),
        green_h   = rgb(160, 220, 130),
        pink      = rgb(230, 150, 170),
        black     = rgb(20, 20, 24),
        stripe    = rgb(98, 100, 108)
    }
}

-- ============================================================================
-- Drawing helpers
-- ============================================================================
local function pset(img, x, y, c)
    if x < 0 or y < 0 or x >= img.width or y >= img.height then return end
    img:drawPixel(x, y, c)
end

local function rect(img, x, y, w, h, c)
    for yy = 0, h - 1 do
        for xx = 0, w - 1 do
            pset(img, x + xx, y + yy, c)
        end
    end
end

local function ellipse(img, cx, cy, rx, ry, c)
    for yy = -ry, ry do
        for xx = -rx, rx do
            local nx = xx / rx
            local ny = yy / ry
            if nx*nx + ny*ny <= 1.0 then pset(img, cx + xx, cy + yy, c) end
        end
    end
end

local function ellipseRing(img, cx, cy, rx, ry, c, thick)
    thick = thick or 1
    for yy = -ry, ry do
        for xx = -rx, rx do
            local nx = xx / rx
            local ny = yy / ry
            local r = nx*nx + ny*ny
            if r <= 1.0 and r >= (1.0 - 0.5 * thick) then pset(img, cx + xx, cy + yy, c) end
        end
    end
end

local function line(img, x0, y0, x1, y1, c)
    local dx = math.abs(x1 - x0); local dy = math.abs(y1 - y0)
    local sx = x0 < x1 and 1 or -1; local sy = y0 < y1 and 1 or -1
    local err = dx - dy
    while true do
        pset(img, x0, y0, c)
        if x0 == x1 and y0 == y1 then break end
        local e2 = 2 * err
        if e2 > -dy then err = err - dy; x0 = x0 + sx end
        if e2 < dx then err = err + dx; y0 = y0 + sy end
    end
end

-- triangle: (x0,y0)-(x1,y1)-(x2,y2)
local function triangle(img, x0, y0, x1, y1, x2, y2, c)
    -- bounding box scan
    local minX = math.min(x0, x1, x2); local maxX = math.max(x0, x1, x2)
    local minY = math.min(y0, y1, y2); local maxY = math.max(y0, y1, y2)
    local function sign(ax, ay, bx, by, cx, cy)
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)
    end
    for y = minY, maxY do
        for x = minX, maxX do
            local d1 = sign(x, y, x0, y0, x1, y1)
            local d2 = sign(x, y, x1, y1, x2, y2)
            local d3 = sign(x, y, x2, y2, x0, y0)
            local hasNeg = d1 < 0 or d2 < 0 or d3 < 0
            local hasPos = d1 > 0 or d2 > 0 or d3 > 0
            if not (hasNeg and hasPos) then pset(img, x, y, c) end
        end
    end
end

-- ============================================================================
-- 32x32 TOP-DOWN IN-GAME SPRITES
-- ============================================================================

local function drawCollieTopDown(img, frame, anim, opts)
    local p = opts.palette
    local stocky = opts.stocky or false
    local bobMap = { idle={0,-1,0,1}, walk={0,1,0,1}, attack={1,0,1}, special={-1,-2,-1} }
    local bob = (bobMap[anim] or {0})[frame + 1] or 0
    local cx = 16
    local cy = 16 + bob

    local bodyW = stocky and 14 or 12
    local bodyH = stocky and 13 or 11

    -- Tail
    local tailWag = (anim == "walk") and ((frame % 2 == 0) and 1 or -1) or 0
    local tx = cx + math.floor(bodyW / 2) + 1
    line(img, tx, cy + 4, tx + 3 + tailWag, cy + 1, p.black)
    line(img, tx, cy + 5, tx + 3 + tailWag, cy + 2, p.white)

    -- Body saddle
    ellipse(img, cx, cy + 1, math.floor(bodyW / 2), math.floor(bodyH / 2), p.black)
    -- Saddle highlight
    ellipse(img, cx, cy, math.floor(bodyW / 2) - 1, math.floor(bodyH / 2) - 2, p.black_h)
    -- Belly white
    ellipse(img, cx, cy + 4, math.floor(bodyW / 2) - 2, math.floor(bodyH / 2) - 2, p.white)

    -- Tan side patches for Charlie
    if p.tan then
        rect(img, cx - 6, cy + 2, 2, 3, p.tan)
        rect(img, cx + 4, cy + 2, 2, 3, p.tan)
    end

    -- Legs
    local legPhase = (anim == "walk") and frame or 0
    local frontOffset = ((legPhase % 2 == 0) and 0 or 1)
    local backOffset = ((legPhase % 2 == 0) and 1 or 0)
    -- Front legs (white)
    rect(img, cx - 4, cy + 6 + frontOffset, 2, 3, p.white)
    rect(img, cx + 2, cy + 6 + frontOffset, 2, 3, p.white)
    -- Back legs (black with tan paw for Charlie)
    rect(img, cx - 5, cy + 6 + backOffset, 2, 3, p.black)
    rect(img, cx + 3, cy + 6 + backOffset, 2, 3, p.black)
    if p.tan_l then
        pset(img, cx - 4, cy + 8 + backOffset, p.tan_l)
        pset(img, cx + 4, cy + 8 + backOffset, p.tan_l)
    end

    -- Head
    local hCx = cx; local hCy = cy - 6
    ellipse(img, hCx, hCy, 5, 4, p.black)
    -- Snout (white blaze)
    rect(img, hCx - 1, hCy - 1, 2, 5, p.white)
    rect(img, hCx, hCy + 3, 2, 1, p.white)
    -- Ears (pricked)
    triangle(img, hCx - 5, hCy - 1, hCx - 6, hCy - 4, hCx - 3, hCy - 2, p.black)
    triangle(img, hCx + 5, hCy - 1, hCx + 6, hCy - 4, hCx + 3, hCy - 2, p.black)
    -- Inner ear pink
    pset(img, hCx - 5, hCy - 2, p.pink)
    pset(img, hCx + 5, hCy - 2, p.pink)
    -- Tan brow markings for Charlie (kabuki)
    if p.tan_h then
        pset(img, hCx - 2, hCy - 2, p.tan_h)
        pset(img, hCx + 1, hCy - 2, p.tan_h)
        pset(img, hCx - 3, hCy - 1, p.tan_h)
        pset(img, hCx + 2, hCy - 1, p.tan_h)
    end
    -- Eyes
    pset(img, hCx - 2, hCy, p.amber)
    pset(img, hCx + 1, hCy, p.amber)
    -- Nose
    pset(img, hCx, hCy + 2, p.nose)

    if anim == "attack" then
        -- Mouth open + bark wave
        pset(img, hCx, hCy + 4, p.pink)
        local r = 3 + frame * 4
        ellipseRing(img, hCx, hCy - 4, r, r, p.amber_h or p.amber)
    elseif anim == "special" then
        -- Speed lines for Zoomies
        for i = 0, 3 do
            pset(img, frame * 2 + 1, cy - 3 + i * 3, p.amber_h or p.amber)
            pset(img, SPRITE - 2 - frame * 2, cy - 3 + i * 3, p.amber_h or p.amber)
        end
    end
end

local function drawKatieTopDown(img, frame, anim)
    local p = PAL.katie
    local bobMap = { idle={0,0,-1,0}, walk={0,1,0,-1}, attack={0,-1,0}, special={-1,-2,-1} }
    local bob = (bobMap[anim] or {0})[frame + 1] or 0
    local cx = 16
    local cy = 16 + bob

    -- Pink top
    rect(img, cx - 5, cy - 2, 11, 8, p.pink)
    -- Highlight
    rect(img, cx - 5, cy - 2, 11, 1, p.pink_h)
    -- Waistband shadow
    rect(img, cx - 5, cy + 5, 11, 1, p.pink_d)

    -- Black leggings
    rect(img, cx - 4, cy + 6, 3, 6, p.black)
    rect(img, cx + 1, cy + 6, 3, 6, p.black)
    -- Sneakers
    rect(img, cx - 4, cy + 12, 3, 1, p.white)
    rect(img, cx + 1, cy + 12, 3, 1, p.white)

    -- Arms
    local armSway = (anim == "walk") and ((frame % 2 == 0) and 0 or 1) or 0
    rect(img, cx - 7, cy - 1 + armSway, 2, 5, p.skin)
    rect(img, cx + 5, cy - 1 - armSway, 2, 5, p.skin)
    -- Watch (yellow)
    pset(img, cx + 5, cy + 4 - armSway, p.watch_face)
    pset(img, cx + 6, cy + 4 - armSway, p.watch_band)

    -- Head
    ellipse(img, cx, cy - 6, 4, 4, p.skin)
    pset(img, cx - 3, cy - 5, p.skin_s)
    pset(img, cx + 3, cy - 5, p.skin_s)

    -- Hair
    rect(img, cx - 4, cy - 11, 8, 3, p.hair)
    rect(img, cx - 4, cy - 11, 8, 1, p.hair_h)
    pset(img, cx - 4, cy - 8, p.hair)
    pset(img, cx + 3, cy - 8, p.hair)
    -- Ponytail (top of head, longer in walk)
    local ptLen = (anim == "walk") and (4 + (frame % 2)) or 4
    rect(img, cx - 1, cy - 8, 2, ptLen, p.hair)

    -- Eyes
    pset(img, cx - 2, cy - 6, p.eye)
    pset(img, cx + 1, cy - 6, p.eye)

    if anim == "attack" then
        local len = 8 + frame * 5
        for i = 0, len do pset(img, cx + 6 + i, cy + 4 - armSway, rgb(255, 80, 80)) end
        pset(img, cx + 5, cy + 4 - armSway, p.watch_face)
    elseif anim == "special" then
        local r = 8 + frame * 2
        ellipseRing(img, cx, cy, r, r, rgb(136, 225, 255, 180))
    end
end

local function drawCatTopDown(img, frame, anim, opts)
    local p = opts.palette
    local big = opts.big or false
    local bobMap = { idle={0,-1,0,0}, walk={0,1,0,1}, attack={0,1,0}, special={-1,-2,-3} }
    local bob = (bobMap[anim] or {0})[frame + 1] or 0
    local cx = 16; local cy = 16 + bob

    local bodyR = big and 7 or 6
    local headR = big and 4 or 3

    -- Tail (curls up)
    local tailWag = (anim == "walk") and ((frame % 2 == 0) and 0 or 1) or 0
    local tx = cx + bodyR + 1 + tailWag
    line(img, tx, cy + 1, tx + 2, cy - 3, p.grey)
    pset(img, tx + 2, cy - 4, p.grey_d)

    -- Body
    ellipse(img, cx, cy + 1, bodyR, bodyR - 1, p.grey)
    -- Highlight
    ellipse(img, cx, cy, bodyR - 2, bodyR - 3, p.grey_h)
    -- White belly
    ellipse(img, cx, cy + 3, bodyR - 2, bodyR - 3, p.white)
    -- Stripes
    if big then
        for i = -3, 3, 2 do
            pset(img, cx + i, cy, p.stripe)
            pset(img, cx + i, cy + 2, p.stripe)
        end
    else
        pset(img, cx - 2, cy, p.stripe)
        pset(img, cx + 2, cy, p.stripe)
    end

    -- Legs
    local legPhase = (anim == "walk") and frame or 0
    local lY = cy + bodyR - 1
    rect(img, cx - bodyR + 2, lY + (legPhase % 2), 2, 2, p.white)
    rect(img, cx + bodyR - 3, lY + ((legPhase + 1) % 2), 2, 2, p.white)

    -- Head
    ellipse(img, cx, cy - bodyR + 2, headR, headR - 1, p.grey)
    -- Highlight
    pset(img, cx - 1, cy - bodyR + 1, p.grey_h)
    pset(img, cx + 1, cy - bodyR + 1, p.grey_h)
    -- Muzzle
    rect(img, cx - 1, cy - bodyR + 4, 2, 1, p.white)

    -- Ears (triangular)
    triangle(img, cx - headR, cy - bodyR + 1, cx - headR - 1, cy - bodyR - 1, cx - headR + 2, cy - bodyR + 1, p.grey)
    triangle(img, cx + headR, cy - bodyR + 1, cx + headR + 1, cy - bodyR - 1, cx + headR - 2, cy - bodyR + 1, p.grey)
    -- Inner ear pink
    pset(img, cx - headR, cy - bodyR + 1, p.pink)
    pset(img, cx + headR - 1, cy - bodyR + 1, p.pink)

    -- Eyes
    pset(img, cx - 2, cy - bodyR + 2, p.green)
    pset(img, cx + 1, cy - bodyR + 2, p.green)
    -- Half-lid for Tia
    if big then
        pset(img, cx - 2, cy - bodyR + 1, p.grey_d)
        pset(img, cx + 1, cy - bodyR + 1, p.grey_d)
    end
    -- Nose
    pset(img, cx, cy - bodyR + 3, p.pink)

    if anim == "attack" then
        for i = 0, 3 do
            local angle = math.pi * (0.65 + i * 0.18 + frame * 0.12)
            local rx = math.floor(math.cos(angle) * (10 + frame))
            local ry = math.floor(math.sin(angle) * (10 + frame))
            pset(img, cx + rx, cy - 5 + ry, p.white)
            pset(img, cx + rx + 1, cy - 5 + ry, p.white)
        end
    elseif anim == "special" then
        if big then
            -- Tia leap arc
            for i = 0, 5 do
                pset(img, cx - 9 + i, cy - bodyR - 1 + i, rgb(255, 240, 168, 180))
                pset(img, cx + 9 - i, cy - bodyR - 1 + i, rgb(255, 240, 168, 180))
            end
        else
            -- Nancy invisibility shimmer
            for y = 0, SPRITE - 1 do
                for x = 0, SPRITE - 1 do
                    if (x + y * 7 + frame * 13) % 11 == 0 then pset(img, x, y, rgb(255,255,255, 90)) end
                end
            end
        end
    end
end

-- ============================================================================
-- 96x96 NATIVE FRONT-FACING PORTRAITS
-- ============================================================================

local function drawCollieFront(img, p, opts)
    local stocky = opts.stocky or false
    local W = img.width
    local H = img.height
    -- Background fade
    rect(img, 0, 0, W, H, rgb(20, 24, 42))

    local cx = W / 2
    local headW = stocky and 36 or 30
    local headH = stocky and 38 or 34
    local hCy = 38

    -- Body / chest at bottom (white V chest, black saddle on shoulders)
    -- Black saddle (across shoulders, top of body)
    local bodyTop = 64
    rect(img, cx - 28, bodyTop, 56, H - bodyTop, p.black)
    -- White chest V shape
    triangle(img, cx - 18, bodyTop - 2, cx + 18, bodyTop - 2, cx, H, p.white)
    -- Belly white expand
    ellipse(img, math.floor(cx), 90, 22, 18, p.white)
    -- Tan side patches
    if p.tan then
        rect(img, cx - 30, bodyTop + 6, 4, 14, p.tan)
        rect(img, cx + 26, bodyTop + 6, 4, 14, p.tan)
    end

    -- Head (large oval, mostly black with white blaze)
    ellipse(img, math.floor(cx), hCy, math.floor(headW/2), math.floor(headH/2), p.black)
    -- Shadow at bottom of head
    ellipse(img, math.floor(cx), hCy + 8, math.floor(headW/2) - 2, math.floor(headH/2) - 6, p.black_h)
    -- Snout/blaze (white stripe down center of face)
    rect(img, cx - 4, hCy - 14, 8, 24, p.white)
    -- Snout shadow
    pset(img, cx - 5, hCy - 4, p.white_s)
    pset(img, cx + 4, hCy - 4, p.white_s)
    -- Snout taper
    triangle(img, cx - 4, hCy + 8, cx + 4, hCy + 8, cx, hCy + 16, p.white)

    -- Ears (pricked, slight outward angle)
    triangle(img, cx - 16, hCy - 16, cx - 22, hCy - 28, cx - 8, hCy - 18, p.black)
    triangle(img, cx + 16, hCy - 16, cx + 22, hCy - 28, cx + 8, hCy - 18, p.black)
    -- Inner ear pink
    triangle(img, cx - 14, hCy - 17, cx - 18, hCy - 24, cx - 10, hCy - 18, p.pink)
    triangle(img, cx + 14, hCy - 17, cx + 18, hCy - 24, cx + 10, hCy - 18, p.pink)
    -- Ear highlight
    pset(img, cx - 17, hCy - 24, p.black_h)
    pset(img, cx + 17, hCy - 24, p.black_h)

    -- Tan brow markings (Charlie - kabuki face)
    if p.tan_h then
        rect(img, cx - 12, hCy - 4, 4, 4, p.tan_h)
        rect(img, cx + 8, hCy - 4, 4, 4, p.tan_h)
        rect(img, cx - 11, hCy - 5, 2, 1, p.tan_l)
        rect(img, cx + 9, hCy - 5, 2, 1, p.tan_l)
    end

    -- Eyes (amber, almond shape)
    rect(img, cx - 12, hCy + 1, 6, 4, p.amber)
    rect(img, cx + 6, hCy + 1, 6, 4, p.amber)
    -- Pupil
    rect(img, cx - 10, hCy + 2, 2, 2, p.black)
    rect(img, cx + 8, hCy + 2, 2, 2, p.black)
    -- Eye shine
    pset(img, cx - 9, hCy + 1, p.white)
    pset(img, cx + 9, hCy + 1, p.white)
    -- Eye outline (top)
    line(img, cx - 12, hCy + 1, cx - 6, hCy + 1, p.black)
    line(img, cx + 6, hCy + 1, cx + 12, hCy + 1, p.black)

    -- Nose (large triangle)
    triangle(img, cx - 4, hCy + 13, cx + 4, hCy + 13, cx, hCy + 18, p.nose)
    -- Nose highlight
    pset(img, cx - 1, hCy + 14, p.black_h)

    -- Mouth (slight smile)
    line(img, cx - 5, hCy + 19, cx, hCy + 21, p.black)
    line(img, cx, hCy + 21, cx + 5, hCy + 19, p.black)
    -- Pink tongue showing
    pset(img, cx - 1, hCy + 21, p.pink)
    pset(img, cx, hCy + 21, p.pink)
    pset(img, cx + 1, hCy + 21, p.pink)
end

local function drawKatieFront(img)
    local p = PAL.katie
    local W = img.width; local H = img.height
    rect(img, 0, 0, W, H, rgb(20, 24, 42))
    local cx = W / 2

    -- Body — pink Lululemon hoodie/crop
    local bodyTop = 56
    -- Outer hoodie shape
    rect(img, cx - 22, bodyTop, 44, H - bodyTop, p.pink)
    -- Highlight stripe on top of body
    rect(img, cx - 22, bodyTop, 44, 3, p.pink_h)
    -- Hoodie collar V
    triangle(img, cx - 8, bodyTop - 2, cx + 8, bodyTop - 2, cx, bodyTop + 12, p.pink_d)
    -- Inner collar (skin showing)
    triangle(img, cx - 5, bodyTop - 1, cx + 5, bodyTop - 1, cx, bodyTop + 8, p.skin)
    -- Hoodie strings
    rect(img, cx - 1, bodyTop, 1, 14, p.white)
    rect(img, cx + 1, bodyTop, 1, 14, p.white)
    -- Tag/logo (lululemon "○" suggestion)
    pset(img, cx + 16, bodyTop + 18, p.white)
    pset(img, cx + 17, bodyTop + 18, p.white)

    -- Apple Watch on right wrist (visible at lower right)
    local wx = cx + 22; local wy = bodyTop + 26
    rect(img, wx, wy, 6, 8, p.watch_band)
    rect(img, wx + 1, wy + 2, 4, 4, p.watch_face)
    pset(img, wx + 2, wy + 3, p.black)
    pset(img, wx + 3, wy + 3, p.black)

    -- Neck
    rect(img, cx - 5, bodyTop - 8, 10, 8, p.skin)
    rect(img, cx - 5, bodyTop - 8, 10, 1, p.skin_s)

    -- Head
    local hCy = 32
    ellipse(img, math.floor(cx), hCy, 18, 22, p.skin)
    -- Cheek shadow / contour
    ellipse(img, math.floor(cx) - 14, hCy + 8, 4, 4, p.skin_s)
    ellipse(img, math.floor(cx) + 14, hCy + 8, 4, 4, p.skin_s)
    -- Jaw highlight
    rect(img, cx - 3, hCy + 18, 6, 2, p.skin_h)

    -- Brunette hair (frame around face, slightly volumed)
    -- Top sweep
    rect(img, cx - 18, hCy - 22, 36, 8, p.hair)
    rect(img, cx - 18, hCy - 22, 36, 2, p.hair_h)
    -- Side fall (left bigger)
    rect(img, cx - 22, hCy - 16, 6, 22, p.hair)
    rect(img, cx + 16, hCy - 16, 6, 22, p.hair)
    -- Hair ear cover
    rect(img, cx - 22, hCy - 16, 4, 2, p.hair_h)
    rect(img, cx + 18, hCy - 16, 4, 2, p.hair_h)
    -- Bangs/fringe
    rect(img, cx - 14, hCy - 14, 28, 5, p.hair)
    rect(img, cx - 14, hCy - 14, 28, 1, p.hair_h)
    -- Ponytail offset to side (sweep over right shoulder)
    rect(img, cx + 18, hCy - 8, 4, 14, p.hair)
    rect(img, cx + 18, hCy - 8, 1, 14, p.hair_h)
    rect(img, cx + 20, hCy + 6, 5, 14, p.hair)
    -- Hair tie
    pset(img, cx + 19, hCy - 6, p.pink)
    pset(img, cx + 20, hCy - 6, p.pink)
    pset(img, cx + 21, hCy - 6, p.pink)

    -- Eyes
    -- Eyebrows
    rect(img, cx - 11, hCy - 6, 5, 2, p.hair)
    rect(img, cx + 6, hCy - 6, 5, 2, p.hair)
    -- Eye whites
    rect(img, cx - 11, hCy - 2, 6, 4, p.white)
    rect(img, cx + 5, hCy - 2, 6, 4, p.white)
    -- Iris (brown)
    rect(img, cx - 9, hCy - 2, 3, 4, p.eye)
    rect(img, cx + 6, hCy - 2, 3, 4, p.eye)
    -- Pupil
    rect(img, cx - 8, hCy - 1, 1, 2, p.black)
    rect(img, cx + 7, hCy - 1, 1, 2, p.black)
    -- Eye shine
    pset(img, cx - 7, hCy - 1, p.white)
    pset(img, cx + 8, hCy - 1, p.white)
    -- Eye top liner
    line(img, cx - 11, hCy - 2, cx - 5, hCy - 2, p.hair)
    line(img, cx + 5, hCy - 2, cx + 11, hCy - 2, p.hair)

    -- Nose
    line(img, cx - 1, hCy + 4, cx - 2, hCy + 8, p.skin_s)
    line(img, cx + 1, hCy + 4, cx + 2, hCy + 8, p.skin_s)
    pset(img, cx, hCy + 9, p.skin_s)

    -- Lips
    rect(img, cx - 4, hCy + 13, 8, 1, p.lip)
    pset(img, cx - 3, hCy + 14, p.lip)
    pset(img, cx + 2, hCy + 14, p.lip)
end

local function drawCatFront(img, opts)
    local p = opts.palette
    local big = opts.big or false
    local W = img.width; local H = img.height
    rect(img, 0, 0, W, H, rgb(20, 24, 42))
    local cx = W / 2

    local headW = big and 50 or 42
    local headH = big and 46 or 40
    local hCy = 44

    -- Chest/body (visible at bottom)
    local bodyTop = 70
    rect(img, cx - (big and 26 or 22), bodyTop, big and 52 or 44, H - bodyTop, p.grey)
    -- White chest fluff
    ellipse(img, math.floor(cx), bodyTop + 14, big and 14 or 12, 14, p.white)

    -- Big round head
    ellipse(img, math.floor(cx), hCy, math.floor(headW/2), math.floor(headH/2), p.grey)
    -- Highlight on top of head
    ellipse(img, math.floor(cx), hCy - 12, math.floor(headW/2) - 6, 8, p.grey_h)
    -- Tabby stripes (only on Tia)
    if big then
        for i = -2, 2 do
            line(img, cx + i * 6, hCy - 18, cx + i * 6 + 1, hCy - 12, p.stripe)
            line(img, cx + i * 6 - 2, hCy - 14, cx + i * 6 + 2, hCy - 14, p.stripe)
        end
    end
    -- Cheek puffs (white below eyes, large for Tia)
    if big then
        ellipse(img, math.floor(cx) - 12, hCy + 6, 10, 8, p.white)
        ellipse(img, math.floor(cx) + 12, hCy + 6, 10, 8, p.white)
    else
        ellipse(img, math.floor(cx) - 9, hCy + 5, 7, 6, p.white)
        ellipse(img, math.floor(cx) + 9, hCy + 5, 7, 6, p.white)
    end

    -- Ears (triangular, BIG cat ears)
    local earH = big and 18 or 16
    local earW = big and 12 or 10
    triangle(img, cx - math.floor(headW/2) + 4, hCy - math.floor(headH/2) + 4,
                  cx - math.floor(headW/2) + 6 - earW, hCy - math.floor(headH/2) + 4 - earH,
                  cx - math.floor(headW/2) + 4 + earW, hCy - math.floor(headH/2) + 4, p.grey)
    triangle(img, cx + math.floor(headW/2) - 4, hCy - math.floor(headH/2) + 4,
                  cx + math.floor(headW/2) - 6 + earW, hCy - math.floor(headH/2) + 4 - earH,
                  cx + math.floor(headW/2) - 4 - earW, hCy - math.floor(headH/2) + 4, p.grey)
    -- Inner ear pink
    triangle(img, cx - math.floor(headW/2) + 6, hCy - math.floor(headH/2) + 4,
                  cx - math.floor(headW/2) + 6 - earW + 4, hCy - math.floor(headH/2) - earH + 8,
                  cx - math.floor(headW/2) + 4 + earW - 2, hCy - math.floor(headH/2) + 4, p.pink)
    triangle(img, cx + math.floor(headW/2) - 6, hCy - math.floor(headH/2) + 4,
                  cx + math.floor(headW/2) - 6 + earW - 4, hCy - math.floor(headH/2) - earH + 8,
                  cx + math.floor(headW/2) - 4 - earW + 2, hCy - math.floor(headH/2) + 4, p.pink)

    -- Eyes (BIG green almond eyes)
    local eyeW = big and 11 or 10
    local eyeH = big and 8 or 9 -- nancy bigger/rounder, tia half-lidded
    -- Eye whites
    ellipse(img, math.floor(cx) - 10, hCy - 2, math.floor(eyeW/2), math.floor(eyeH/2), p.white)
    ellipse(img, math.floor(cx) + 10, hCy - 2, math.floor(eyeW/2), math.floor(eyeH/2), p.white)
    -- Iris (green)
    ellipse(img, math.floor(cx) - 10, hCy - 2, math.floor(eyeW/2) - 1, math.floor(eyeH/2) - 1, p.green)
    ellipse(img, math.floor(cx) + 10, hCy - 2, math.floor(eyeW/2) - 1, math.floor(eyeH/2) - 1, p.green)
    -- Iris highlight
    pset(img, cx - 11, hCy - 4, p.green_h)
    pset(img, cx + 9, hCy - 4, p.green_h)
    -- Pupil (vertical slit for cat)
    rect(img, cx - 10, hCy - 4, 1, 6, p.black)
    rect(img, cx + 10, hCy - 4, 1, 6, p.black)
    -- Eye shine
    pset(img, cx - 9, hCy - 3, p.white)
    pset(img, cx + 11, hCy - 3, p.white)

    -- Half-lid for Tia (big confident cat)
    if big then
        rect(img, cx - 14, hCy - 6, 8, 2, p.grey_d)
        rect(img, cx + 6, hCy - 6, 8, 2, p.grey_d)
    end

    -- Nose (pink triangle)
    triangle(img, cx - 3, hCy + 8, cx + 3, hCy + 8, cx, hCy + 12, p.pink)
    pset(img, cx - 1, hCy + 9, rgb(255, 200, 215))

    -- Mouth
    line(img, cx, hCy + 13, cx - 4, hCy + 16, p.grey_d)
    line(img, cx, hCy + 13, cx + 4, hCy + 16, p.grey_d)

    -- Whiskers (white lines)
    line(img, cx - 14, hCy + 6, cx - 24, hCy + 4, p.white_s)
    line(img, cx - 14, hCy + 9, cx - 24, hCy + 10, p.white_s)
    line(img, cx + 14, hCy + 6, cx + 24, hCy + 4, p.white_s)
    line(img, cx + 14, hCy + 9, cx + 24, hCy + 10, p.white_s)
end

-- ============================================================================
-- ENEMIES (32x32 top-down)
-- ============================================================================

local function drawPeloton(img, frame, anim)
    local cx = 16
    local cy = 16
    local helmet = rgb(255, 31, 75)
    local frame_color = rgb(40, 40, 48)
    local jersey = rgb(255, 80, 110)
    local skin = rgb(241, 199, 165)
    local wheel = rgb(20, 20, 24)
    local rim = rgb(160, 160, 168)

    -- Wheels (top + bottom)
    ellipse(img, cx, cy - 9, 4, 4, wheel)
    ellipseRing(img, cx, cy - 9, 4, 4, rim, 1)
    ellipse(img, cx, cy + 10, 4, 4, wheel)
    ellipseRing(img, cx, cy + 10, 4, 4, rim, 1)
    -- Frame
    rect(img, cx - 1, cy - 6, 2, 14, frame_color)
    -- Rider torso (hot pink jersey leaning forward)
    ellipse(img, cx, cy + 1, 4, 5, jersey)
    pset(img, cx - 2, cy - 1, rgb(255, 255, 255)) -- racing stripe
    pset(img, cx + 1, cy - 1, rgb(255, 255, 255))
    -- Arms gripping
    rect(img, cx - 4, cy - 4, 2, 4, skin)
    rect(img, cx + 2, cy - 4, 2, 4, skin)
    -- Helmet
    ellipse(img, cx, cy - 5, 3, 3, helmet)
    pset(img, cx, cy - 7, rgb(255, 255, 255)) -- helmet vent
    -- Speed lines
    if anim ~= "idle" then
        for i = 0, 2 do
            pset(img, frame * 2 + i, cy - 2, rgb(180, 180, 200))
            pset(img, 31 - frame * 2 - i, cy + 4, rgb(180, 180, 200))
        end
    end
end

local function drawLeash(img, frame, anim)
    -- Horizontal red retractable leash. The "enemy" stretches the full 48px width
    -- but we draw a 32x32 frame; the engine scales it to GAME_WIDTH.
    local handle = rgb(60, 60, 64)
    local handle_h = rgb(120, 120, 128)
    local cord = rgb(208, 72, 72)
    local cord_h = rgb(255, 130, 130)
    local dog = rgb(123, 74, 30)
    local dog_h = rgb(180, 120, 60)
    local cy = 16

    -- Cord across
    rect(img, 0, cy - 1, 32, 2, cord)
    rect(img, 0, cy, 32, 1, cord_h)
    -- Handle (left)
    rect(img, 1, cy - 4, 6, 8, handle)
    rect(img, 1, cy - 4, 6, 1, handle_h)
    rect(img, 1, cy + 3, 6, 1, rgb(20, 20, 24))
    -- Dog blob (right)
    ellipse(img, 26, cy, 4, 5, dog)
    ellipse(img, 26, cy - 1, 3, 3, dog_h)
    pset(img, 24, cy - 1, rgb(255, 255, 255)) -- eye
    pset(img, 28, cy - 1, rgb(255, 255, 255)) -- eye
    pset(img, 24, cy, rgb(20, 20, 24))
    pset(img, 28, cy, rgb(20, 20, 24))
    if anim ~= "idle" then
        rect(img, 0, cy - 2 - frame, 32, 1, rgb(255, 255, 255))
    end
end

local function drawCoffee(img, frame, anim)
    local cx = 16; local cy = 16
    local coffee = rgb(90, 58, 31)
    local coffee_d = rgb(58, 31, 10)
    local foam = rgb(245, 240, 220)
    local ice = rgb(180, 220, 240)
    -- Splatter drops
    pset(img, cx - 12, cy - 3, coffee)
    pset(img, cx + 12, cy + 3, coffee)
    pset(img, cx - 8, cy + 10, coffee)
    pset(img, cx + 8, cy - 10, coffee)
    -- Main puddle
    ellipse(img, cx, cy, 11 + (frame % 2), 9 + (frame % 2), coffee)
    ellipse(img, cx, cy, 8, 6, coffee_d)
    -- Ice cubes
    rect(img, cx - 4, cy - 3, 3, 3, ice)
    rect(img, cx + 1, cy + 1, 3, 3, ice)
    rect(img, cx - 3, cy - 2, 1, 1, foam)
    rect(img, cx + 2, cy + 2, 1, 1, foam)
    -- Straw
    line(img, cx - 1, cy - 5, cx + 4, cy - 9, rgb(255, 80, 110))
    line(img, cx, cy - 5, cx + 5, cy - 9, rgb(255, 100, 130))
    if anim == "attack" or anim == "special" then
        ellipseRing(img, cx, cy, 12 + frame, 10 + frame, foam)
    end
end

-- ============================================================================
-- BOSS — The Main Character / Influencer (64x64)
-- ============================================================================

local function drawInfluencer(img, frame, anim)
    local cx = 32; local cy = 36
    local bg = rgb(20, 24, 42, 0)
    rect(img, 0, 0, img.width, img.height, bg)

    local skin = rgb(241, 199, 165)
    local skin_s = rgb(208, 156, 122)
    local hair = rgb(255, 224, 102) -- blonde
    local hair_h = rgb(255, 240, 160)
    local lash = rgb(20, 20, 24)
    local pink = rgb(248, 182, 203)
    local pink_d = rgb(220, 138, 165)
    local lip = rgb(220, 80, 100)
    local sunglass = rgb(20, 20, 24)
    local sunglass_h = rgb(80, 80, 88)
    local phone = rgb(40, 40, 48)
    local phone_screen = rgb(170, 220, 255)

    -- Body (pink crop top)
    rect(img, cx - 14, cy + 6, 28, 24, pink)
    rect(img, cx - 14, cy + 6, 28, 2, rgb(255, 220, 235))
    rect(img, cx - 14, cy + 28, 28, 2, pink_d)

    -- Head
    ellipse(img, cx, cy, 11, 13, skin)
    -- Cheek shadow
    ellipse(img, cx - 8, cy + 4, 3, 3, skin_s)
    ellipse(img, cx + 8, cy + 4, 3, 3, skin_s)

    -- Long blonde hair (over shoulders)
    rect(img, cx - 15, cy - 16, 30, 9, hair)
    rect(img, cx - 15, cy - 16, 30, 2, hair_h)
    rect(img, cx - 18, cy - 8, 8, 28, hair)
    rect(img, cx + 10, cy - 8, 8, 28, hair)
    rect(img, cx - 18, cy - 8, 1, 28, hair_h)
    rect(img, cx + 17, cy - 8, 1, 28, hair_h)
    -- Center part
    rect(img, cx, cy - 16, 1, 4, rgb(220, 195, 80))

    -- Sunglasses (large rectangular)
    rect(img, cx - 9, cy - 4, 18, 6, sunglass)
    rect(img, cx - 9, cy - 4, 18, 1, sunglass_h)
    -- Bridge
    pset(img, cx, cy - 3, sunglass)
    pset(img, cx, cy - 2, sunglass)
    -- Lens reflection
    pset(img, cx - 7, cy - 3, sunglass_h)
    pset(img, cx + 4, cy - 3, sunglass_h)

    -- Lips (pouty)
    rect(img, cx - 4, cy + 5, 8, 2, lip)
    pset(img, cx - 4, cy + 6, rgb(180, 60, 80))
    pset(img, cx + 3, cy + 6, rgb(180, 60, 80))
    pset(img, cx, cy + 7, lip)

    -- Right arm raised holding phone (the WEAK POINT)
    rect(img, cx + 13, cy - 4, 4, 12, skin)
    -- Phone (held up at angle)
    local phoneOffsetX = 0; local phoneOffsetY = 0
    if anim == "attack" then
        phoneOffsetX = (frame % 2 == 0) and -1 or 1
    end
    rect(img, cx + 18 + phoneOffsetX, cy - 12 + phoneOffsetY, 6, 10, phone)
    rect(img, cx + 19 + phoneOffsetX, cy - 11 + phoneOffsetY, 4, 8, phone_screen)
    -- Camera lens on phone
    pset(img, cx + 20 + phoneOffsetX, cy - 10 + phoneOffsetY, rgb(220, 220, 230))
    pset(img, cx + 21 + phoneOffsetX, cy - 10 + phoneOffsetY, rgb(220, 220, 230))
    pset(img, cx + 20 + phoneOffsetX, cy - 9 + phoneOffsetY, rgb(80, 80, 90))
    pset(img, cx + 21 + phoneOffsetX, cy - 9 + phoneOffsetY, rgb(80, 80, 90))

    -- Selfie flash on attack frames
    if anim == "attack" then
        ellipse(img, cx + 21 + phoneOffsetX, cy - 10 + phoneOffsetY, 4 + frame * 2, 4 + frame * 2, rgb(255, 255, 255, 200))
    end
    -- Walk = swaying
    if anim == "walk" then
        if frame % 2 == 1 then
            rect(img, cx + 18, cy - 13, 6, 11, phone)
        end
    end
    -- Special = halo aura
    if anim == "special" then
        ellipseRing(img, cx, cy, 18 + frame * 4, 20 + frame * 4, rgb(255, 215, 0, 180))
    end

    -- Left arm at hip
    rect(img, cx - 17, cy + 4, 4, 10, skin)
end

-- ============================================================================
-- TILE — Katy Trail (64x64 seamless)
-- ============================================================================

local function drawKatyTrailTile(img)
    local W = img.width; local H = img.height
    local concrete_d = rgb(150, 148, 138)
    local concrete = rgb(178, 176, 165)
    local concrete_h = rgb(200, 198, 188)
    local grass = rgb(58, 130, 52)
    local grass_d = rgb(38, 100, 36)
    local grass_h = rgb(98, 168, 80)
    local yellow = rgb(240, 200, 30)
    local yellow_d = rgb(180, 145, 20)
    local crack = rgb(120, 118, 110)

    for y = 0, H - 1 do
        for x = 0, W - 1 do
            if x >= 12 and x <= W - 13 then
                -- Concrete path with subtle noise
                local n = ((x * 31 + y * 17) % 13)
                if n < 4 then pset(img, x, y, concrete_d)
                elseif n > 9 then pset(img, x, y, concrete_h)
                else pset(img, x, y, concrete) end
            else
                -- Grass with subtle variation
                local n = ((x * 7 + y * 11) % 7)
                if n == 0 then pset(img, x, y, grass_d)
                elseif n == 1 then pset(img, x, y, grass_h)
                else pset(img, x, y, grass) end
            end
        end
    end
    -- Concrete crack lines
    for x = 0, W - 1 do
        pset(img, x, 0, concrete_d)
        pset(img, x, H - 1, concrete_d)
    end
    -- Yellow center line (dashed, seamless top/bottom)
    for y = 0, H - 1 do
        if (y % 16) < 8 then
            rect(img, W / 2 - 1, y, 3, 1, yellow)
            pset(img, W / 2 - 1, y, yellow_d)
            pset(img, W / 2 + 1, y, yellow_d)
        end
    end
    -- Random pebbles in grass (seeded so seamless)
    local seed = 17
    for i = 1, 12 do
        seed = (seed * 31 + 7) % 1009
        local x = (seed * 13) % W
        local y = (seed * 19) % H
        if x < 11 or x > W - 12 then
            pset(img, x, y, rgb(220, 220, 215))
        end
    end
    -- Grass tufts on edges
    for x = 0, W - 1, 5 do
        pset(img, x % 11 + 4, x % H, grass_h)
        pset(img, W - 1 - (x % 11 + 4), (x + 13) % H, grass_h)
    end
end

-- ============================================================================
-- Builders
-- ============================================================================

local ANIM_DEF = {
    { name = "idle",    count = 4 },
    { name = "walk",    count = 4 },
    { name = "attack",  count = 3 },
    { name = "special", count = 3 }
}

local function buildAnimSheet(spec)
    local total = 0
    for _, a in ipairs(ANIM_DEF) do total = total + a.count end

    local sprite = Sprite(spec.size, spec.size, ColorMode.RGB)
    for i = 2, total do app.command.NewFrame() end

    local idx = 1
    for _, a in ipairs(ANIM_DEF) do
        for fi = 0, a.count - 1 do
            local cel = sprite.cels[idx]
            local img = Image(spec.size, spec.size, ColorMode.RGB)
            spec.draw(img, fi, a.name)
            cel.image = img
            idx = idx + 1
        end
    end

    local cursor = 1
    for _, a in ipairs(ANIM_DEF) do
        local tag = sprite:newTag(cursor, cursor + a.count - 1)
        tag.name = a.name
        cursor = cursor + a.count
    end

    sprite:saveAs(spec.dir .. "/" .. spec.id .. ".aseprite")
    app.command.ExportSpriteSheet {
        ui = false,
        type = SpriteSheetType.ROWS,
        columns = 4,
        textureFilename = spec.dir .. "/" .. spec.id .. ".png",
        dataFilename    = spec.dir .. "/" .. spec.id .. ".json",
        dataFormat = SpriteSheetDataFormat.JSON_HASH,
        filenameFormat = "{tag}_{tagframe}",
        listTags = true
    }
    sprite:close()
    print("✓ " .. spec.dir .. "/" .. spec.id)
end

local function buildPortrait(id, drawFn)
    local sprite = Sprite(PORTRAIT, PORTRAIT, ColorMode.RGB)
    local img = Image(PORTRAIT, PORTRAIT, ColorMode.RGB)
    drawFn(img)
    sprite.cels[1].image = img
    sprite:saveAs(OUT_PORTRAITS .. "/" .. id .. ".png")
    sprite:close()
    print("✓ portraits/" .. id)
end

local function buildTile()
    local sprite = Sprite(64, 64, ColorMode.RGB)
    local img = Image(64, 64, ColorMode.RGB)
    drawKatyTrailTile(img)
    sprite.cels[1].image = img
    sprite:saveAs(OUT_TILES .. "/katy_trail.png")
    sprite:close()
    print("✓ tiles/katy_trail")
end

-- ============================================================================
-- Run
-- ============================================================================

-- Characters
buildAnimSheet { id = "rosie",   dir = OUT_CHARS, size = SPRITE,
    draw = function(img, f, a) drawCollieTopDown(img, f, a, { palette = PAL.rosie }) end }
buildAnimSheet { id = "charlie", dir = OUT_CHARS, size = SPRITE,
    draw = function(img, f, a) drawCollieTopDown(img, f, a, { palette = PAL.charlie, stocky = true }) end }
buildAnimSheet { id = "katie",   dir = OUT_CHARS, size = SPRITE, draw = drawKatieTopDown }
buildAnimSheet { id = "tia",     dir = OUT_CHARS, size = SPRITE,
    draw = function(img, f, a) drawCatTopDown(img, f, a, { palette = PAL.tia, big = true }) end }
buildAnimSheet { id = "nancy",   dir = OUT_CHARS, size = SPRITE,
    draw = function(img, f, a) drawCatTopDown(img, f, a, { palette = PAL.nancy, big = false }) end }

-- Portraits (96x96 native front-facing)
buildPortrait("rosie",   function(img) drawCollieFront(img, PAL.rosie, {}) end)
buildPortrait("charlie", function(img) drawCollieFront(img, PAL.charlie, { stocky = true }) end)
buildPortrait("katie",   drawKatieFront)
buildPortrait("tia",     function(img) drawCatFront(img, { palette = PAL.tia, big = true }) end)
buildPortrait("nancy",   function(img) drawCatFront(img, { palette = PAL.nancy, big = false }) end)

-- Enemies
buildAnimSheet { id = "peloton", dir = OUT_ENEMIES, size = SPRITE, draw = drawPeloton }
buildAnimSheet { id = "leash",   dir = OUT_ENEMIES, size = SPRITE, draw = drawLeash }
buildAnimSheet { id = "coffee",  dir = OUT_ENEMIES, size = SPRITE, draw = drawCoffee }

-- Boss (64x64)
buildAnimSheet { id = "main_character", dir = OUT_BOSSES, size = 64, draw = drawInfluencer }

-- Tile
buildTile()

print("")
print("All assets generated.")
