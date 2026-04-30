-- Suburban Scramble: Dallas Edition — Rosie body parts for Spine rigging
-- Run from project root with:
--   /Applications/Aseprite.app/Contents/MacOS/aseprite -b --script scripts/aseprite/rosie_spine_parts.lua
--
-- Outputs 8 transparent PNGs into static/assets/spine/rosie/parts/ for the
-- Genielabs spine-animation-ai pipeline to atlas + rig:
--   body.png, head.png, ear-left.png, ear-right.png, tail.png,
--   leg-front-left.png, leg-front-right.png, leg-back-left.png, leg-back-right.png
-- Plus an assembled reference image at static/assets/spine/rosie/reference.png
-- so SIFT-based positioners can find each part on the assembled body.
--
-- View: top-down 3/4 (Rosie facing UP, the direction enemies come from).
-- Style: thick black outlines + flat saturated fills (Pajama Sam vocabulary).

local OUT = "static/assets/spine/rosie/parts"
local REF = "static/assets/spine/rosie/reference.png"
local PART_W, PART_H = 256, 256
local REF_W, REF_H = 384, 512

-- ──────────────────────────────────────────────────────────────────────────────
-- Palette (Pajama-Sam-style: saturated, flat, no gradients)
-- ──────────────────────────────────────────────────────────────────────────────
local function rgb(r, g, b, a) return Color{ r=r, g=g, b=b, a=(a or 255) } end

local C = {
    outline   = rgb(15, 15, 18),
    black     = rgb(28, 28, 32),
    black_h   = rgb(60, 60, 70),    -- subtle highlight on the saddle
    white     = rgb(248, 246, 240),
    white_s   = rgb(210, 208, 200), -- belly/blaze shadow
    amber     = rgb(255, 176, 0),
    amber_h   = rgb(255, 220, 120),
    pink      = rgb(228, 130, 152), -- inner-ear, tongue
    pink_d    = rgb(190, 90, 110),
    nose      = rgb(28, 22, 28),
    shadow    = rgb(0, 0, 0, 60)
}

-- ──────────────────────────────────────────────────────────────────────────────
-- Drawing helpers (operate on a given Image)
-- ──────────────────────────────────────────────────────────────────────────────
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

local function ellipseOutline(img, cx, cy, rx, ry, c, thick)
    thick = thick or 4
    for yy = -ry - thick, ry + thick do
        for xx = -rx - thick, rx + thick do
            local nx = xx / rx
            local ny = yy / ry
            local r2 = nx*nx + ny*ny
            local nx2 = xx / (rx + thick)
            local ny2 = yy / (ry + thick)
            local rOuter = nx2*nx2 + ny2*ny2
            if rOuter <= 1.0 and r2 >= 1.0 then pset(img, cx + xx, cy + yy, c) end
        end
    end
end

local function line(img, x0, y0, x1, y1, c, thick)
    thick = thick or 1
    local dx = math.abs(x1 - x0); local dy = math.abs(y1 - y0)
    local sx = x0 < x1 and 1 or -1; local sy = y0 < y1 and 1 or -1
    local err = dx - dy
    while true do
        for tx = -thick + 1, thick - 1 do
            for ty = -thick + 1, thick - 1 do
                pset(img, x0 + tx, y0 + ty, c)
            end
        end
        if x0 == x1 and y0 == y1 then break end
        local e2 = 2 * err
        if e2 > -dy then err = err - dy; x0 = x0 + sx end
        if e2 < dx then err = err + dx; y0 = y0 + sy end
    end
end

local function triangle(img, x0, y0, x1, y1, x2, y2, c)
    local minX = math.floor(math.min(x0, x1, x2))
    local maxX = math.ceil(math.max(x0, x1, x2))
    local minY = math.floor(math.min(y0, y1, y2))
    local maxY = math.ceil(math.max(y0, y1, y2))
    local function sgn(ax, ay, bx, by, cx, cy)
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)
    end
    for y = minY, maxY do
        for x = minX, maxX do
            local d1 = sgn(x, y, x0, y0, x1, y1)
            local d2 = sgn(x, y, x1, y1, x2, y2)
            local d3 = sgn(x, y, x2, y2, x0, y0)
            local hasNeg = d1 < 0 or d2 < 0 or d3 < 0
            local hasPos = d1 > 0 or d2 > 0 or d3 > 0
            if not (hasNeg and hasPos) then pset(img, x, y, c) end
        end
    end
end

-- Black outline pass — for any non-transparent pixel, draw outline color in
-- adjacent transparent pixels. Gives the Pajama-Sam thick-outline look.
local function outlinePass(img, thickness, color)
    thickness = thickness or 4
    local W, H = img.width, img.height
    -- Build a mask of currently-opaque pixels
    local opaque = {}
    for y = 0, H - 1 do
        opaque[y] = {}
        for x = 0, W - 1 do
            local px = img:getPixel(x, y)
            opaque[y][x] = (app.pixelColor.rgbaA(px) > 64)
        end
    end
    for y = 0, H - 1 do
        for x = 0, W - 1 do
            if not opaque[y][x] then
                local found = false
                for dy = -thickness, thickness do
                    for dx = -thickness, thickness do
                        local nx, ny = x + dx, y + dy
                        if nx >= 0 and ny >= 0 and nx < W and ny < H and opaque[ny] and opaque[ny][nx] then
                            if dx*dx + dy*dy <= thickness * thickness then
                                found = true
                                break
                            end
                        end
                    end
                    if found then break end
                end
                if found then pset(img, x, y, color) end
            end
        end
    end
end

-- ──────────────────────────────────────────────────────────────────────────────
-- Body parts
-- ──────────────────────────────────────────────────────────────────────────────

-- Body (torso seen from above): black saddle on top, white belly visible below
-- Pivot at bottom-center (where the rear/tail end is). Image is 256×256.
local function drawBody(img)
    local cx = PART_W / 2
    local cy = PART_H / 2
    -- Belly (white, larger) — slightly elongated
    ellipse(img, cx, cy + 18, 64, 88, C.white)
    -- Saddle (black) on top
    ellipse(img, cx, cy - 8, 56, 72, C.black)
    -- Subtle highlight stripe on saddle
    ellipse(img, cx, cy - 18, 30, 18, C.black_h)
    -- White edge of belly visible beyond the saddle
    -- (already covered by belly drawn first, then saddle on top)
    -- Outline pass last
    outlinePass(img, 5, C.outline)
end

-- Head (top-down): mostly black with a vertical white blaze, two amber eyes,
-- a black nose pointing UP (forward in our scrolling shooter).
-- Pivot at bottom-center (where neck joins body).
local function drawHead(img)
    local cx = PART_W / 2
    local cy = PART_H / 2
    -- Black head (oval with snout extending up)
    ellipse(img, cx, cy + 10, 64, 70, C.black)
    -- Snout pushing forward (up)
    ellipse(img, cx, cy - 50, 30, 36, C.black)
    -- White blaze down center
    rect(img, cx - 12, cy - 80, 24, 110, C.white)
    -- Blaze taper at top (snout tip)
    triangle(img, cx - 14, cy - 70, cx + 14, cy - 70, cx, cy - 90, C.white)
    -- Eyes (amber)
    ellipse(img, cx - 26, cy - 16, 8, 10, C.amber)
    ellipse(img, cx + 26, cy - 16, 8, 10, C.amber)
    -- Pupils (black)
    ellipse(img, cx - 26, cy - 14, 4, 5, C.black)
    ellipse(img, cx + 26, cy - 14, 4, 5, C.black)
    -- Eye shines (white)
    ellipse(img, cx - 28, cy - 18, 2, 2, C.white)
    ellipse(img, cx + 24, cy - 18, 2, 2, C.white)
    -- Eyebrows (subtle amber strokes)
    line(img, cx - 32, cy - 28, cx - 20, cy - 26, C.amber_h, 2)
    line(img, cx + 20, cy - 26, cx + 32, cy - 28, C.amber_h, 2)
    -- Nose (black triangle at snout tip)
    triangle(img, cx - 8, cy - 78, cx + 8, cy - 78, cx, cy - 70, C.nose)
    -- Mouth (small line below nose)
    line(img, cx - 6, cy - 64, cx, cy - 62, C.outline, 2)
    line(img, cx, cy - 62, cx + 6, cy - 64, C.outline, 2)
    -- Pink tongue tip
    pset(img, cx, cy - 60, C.pink)
    pset(img, cx - 1, cy - 60, C.pink)
    pset(img, cx + 1, cy - 60, C.pink)
    -- Outline
    outlinePass(img, 5, C.outline)
end

-- Ear (single, left or right). Pivot at bottom-inner corner (where ear meets head).
-- Drawing the LEFT ear; the right is just a horizontal flip in the rig.
local function drawEar(img, mirrorX)
    mirrorX = mirrorX or false
    local cx = PART_W / 2
    local cy = PART_H / 2
    -- A pricked triangular ear pointing up-and-out
    local x0, y0 = cx + 30, cy + 70  -- inner-bottom (pivot)
    local x1, y1 = cx - 30, cy + 30  -- outer-bottom
    local x2, y2 = cx - 5,  cy - 70  -- top point
    if mirrorX then
        x0 = PART_W - x0
        x1 = PART_W - x1
        x2 = PART_W - x2
    end
    triangle(img, x0, y0, x1, y1, x2, y2, C.black)
    -- Inner pink fold
    local function lerp(a, b, t) return a + (b - a) * t end
    triangle(img,
        lerp(x0, x2, 0.15), lerp(y0, y2, 0.15),
        lerp(x1, x2, 0.30), lerp(y1, y2, 0.30),
        lerp(x0, x2, 0.85), lerp(y0, y2, 0.85),
        C.pink)
    outlinePass(img, 5, C.outline)
end

-- Tail (long, with white tip). Pivot at thick base.
local function drawTail(img)
    local cx = PART_W / 2
    -- Tail base near top (pivot point), curling down-and-right
    -- Draw as a chain of overlapping circles for organic shape
    local pts = {
        {cx, 48,        20},
        {cx + 4, 80,    18},
        {cx + 14, 110,  16},
        {cx + 26, 138,  14},
        {cx + 42, 162,  12},
        {cx + 58, 184,  10},
        {cx + 74, 200,  9}
    }
    for _, p in ipairs(pts) do
        ellipse(img, p[1], p[2], p[3], p[3], C.black)
    end
    -- White tip (final 2 segments)
    ellipse(img, pts[6][1], pts[6][2], pts[6][3] - 1, pts[6][3] - 1, C.white)
    ellipse(img, pts[7][1], pts[7][2], pts[7][3], pts[7][3], C.white)
    outlinePass(img, 5, C.outline)
end

-- Leg (small visible from above). Used for all 4 legs at slightly different
-- positions — Spine handles placement & rotation. Pivot at top-center.
local function drawLeg(img, isFront, isWhite)
    local cx = PART_W / 2
    -- A short stubby leg with a paw at the bottom
    local upperColor = isWhite and C.white or C.black
    local pawColor = C.white
    -- Upper leg
    rect(img, cx - 14, 48, 28, 60, upperColor)
    -- Round joint
    ellipse(img, cx, 48, 16, 12, upperColor)
    -- Lower leg + paw
    ellipse(img, cx, 116, 16, 14, upperColor)
    -- Paw (white)
    ellipse(img, cx, 130, 18, 12, pawColor)
    -- Paw pads (3 small dots)
    pset(img, cx - 6, 134, C.outline)
    pset(img, cx, 136, C.outline)
    pset(img, cx + 6, 134, C.outline)
    outlinePass(img, 5, C.outline)
end

-- ──────────────────────────────────────────────────────────────────────────────
-- Reference (assembled Rosie). Helps the SIFT positioner; also a sanity check.
-- ──────────────────────────────────────────────────────────────────────────────
local function drawReference(img)
    -- Background (transparent)
    -- Draw parts in z-order: legs → body → tail → head → ears
    local cx = REF_W / 2
    local cy = REF_H / 2

    -- Ground shadow ellipse (dark)
    ellipse(img, cx, cy + 130, 90, 14, C.shadow)

    -- Back legs
    -- (left back)
    rect(img, cx - 60, cy + 70, 22, 50, C.black)
    ellipse(img, cx - 49, cy + 120, 14, 10, C.white)
    -- (right back)
    rect(img, cx + 38, cy + 70, 22, 50, C.black)
    ellipse(img, cx + 49, cy + 120, 14, 10, C.white)

    -- Front legs
    -- (left front)
    rect(img, cx - 50, cy - 30, 20, 60, C.white)
    ellipse(img, cx - 40, cy + 30, 13, 9, C.white)
    -- (right front)
    rect(img, cx + 30, cy - 30, 20, 60, C.white)
    ellipse(img, cx + 40, cy + 30, 13, 9, C.white)

    -- Body (saddle on top, belly visible at sides+bottom)
    -- Belly first (white, wider)
    ellipse(img, cx, cy + 30, 80, 100, C.white)
    -- Saddle (black, smaller, centered higher)
    ellipse(img, cx, cy + 5, 70, 80, C.black)

    -- Tail behind body (curling down-right)
    do
        local pts = {
            {cx + 60, cy + 90,  16},
            {cx + 78, cy + 100, 14},
            {cx + 94, cy + 108, 12},
            {cx + 108, cy + 116, 10},
            {cx + 120, cy + 122, 9}
        }
        for i, p in ipairs(pts) do
            local col = (i >= 4) and C.white or C.black
            ellipse(img, p[1], p[2], p[3], p[3], col)
        end
    end

    -- Head (in front of body, pointing UP/forward)
    local hCx = cx
    local hCy = cy - 80
    -- Black head
    ellipse(img, hCx, hCy + 8, 56, 64, C.black)
    -- Snout
    ellipse(img, hCx, hCy - 38, 26, 32, C.black)
    -- White blaze
    rect(img, hCx - 10, hCy - 64, 20, 90, C.white)
    triangle(img, hCx - 12, hCy - 60, hCx + 12, hCy - 60, hCx, hCy - 78, C.white)
    -- Eyes
    ellipse(img, hCx - 22, hCy - 8, 7, 9, C.amber)
    ellipse(img, hCx + 22, hCy - 8, 7, 9, C.amber)
    ellipse(img, hCx - 22, hCy - 6, 3, 4, C.black)
    ellipse(img, hCx + 22, hCy - 6, 3, 4, C.black)
    -- Nose
    triangle(img, hCx - 7, hCy - 66, hCx + 7, hCy - 66, hCx, hCy - 60, C.nose)

    -- Ears (left then right, both pricked)
    triangle(img, hCx - 35, hCy - 28, hCx - 60, hCy - 60, hCx - 25, hCy - 70, C.black)
    triangle(img, hCx + 35, hCy - 28, hCx + 60, hCy - 60, hCx + 25, hCy - 70, C.black)
    -- Inner-ear pink
    triangle(img, hCx - 36, hCy - 36, hCx - 50, hCy - 56, hCx - 30, hCy - 64, C.pink)
    triangle(img, hCx + 36, hCy - 36, hCx + 50, hCy - 56, hCx + 30, hCy - 64, C.pink)

    outlinePass(img, 5, C.outline)
end

-- ──────────────────────────────────────────────────────────────────────────────
-- Save helper
-- ──────────────────────────────────────────────────────────────────────────────
local function saveImage(img, dir, name)
    local sprite = Sprite(img.width, img.height, ColorMode.RGB)
    sprite.cels[1].image = img
    sprite:saveAs(dir .. "/" .. name .. ".png")
    sprite:close()
    print("✓ " .. dir .. "/" .. name .. ".png")
end

-- ──────────────────────────────────────────────────────────────────────────────
-- Run
-- ──────────────────────────────────────────────────────────────────────────────
local parts = {
    {name = "body",            draw = drawBody, w = PART_W, h = PART_H},
    {name = "head",            draw = drawHead, w = PART_W, h = PART_H},
    {name = "ear-left",        draw = function(img) drawEar(img, false) end, w = PART_W, h = PART_H},
    {name = "ear-right",       draw = function(img) drawEar(img, true) end, w = PART_W, h = PART_H},
    {name = "tail",            draw = drawTail, w = PART_W, h = PART_H},
    {name = "leg-front-left",  draw = function(img) drawLeg(img, true, true) end, w = PART_W, h = PART_H},
    {name = "leg-front-right", draw = function(img) drawLeg(img, true, true) end, w = PART_W, h = PART_H},
    {name = "leg-back-left",   draw = function(img) drawLeg(img, false, false) end, w = PART_W, h = PART_H},
    {name = "leg-back-right",  draw = function(img) drawLeg(img, false, false) end, w = PART_W, h = PART_H}
}

for _, p in ipairs(parts) do
    local img = Image(p.w, p.h, ColorMode.RGB)
    p.draw(img)
    saveImage(img, OUT, p.name)
end

-- Reference image
do
    local img = Image(REF_W, REF_H, ColorMode.RGB)
    drawReference(img)
    local sprite = Sprite(img.width, img.height, ColorMode.RGB)
    sprite.cels[1].image = img
    sprite:saveAs(REF)
    sprite:close()
    print("✓ " .. REF)
end

print("\nDone. " .. #parts .. " parts + reference written.")
