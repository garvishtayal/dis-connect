// Extracts the 1x T-Rex sprite already embedded in dino-game.html,
// crops to the standing frame (x=44, 44×47px) and writes favicon.svg.
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

const html = readFileSync(join(root, 'public/dino-game.html'), 'utf8')
const match = html.match(/id="1x-trex"\s+src="(data:image\/png;base64,[^"]+)"/)
if (!match) throw new Error('1x-trex sprite not found in dino-game.html')

const dataUri = match[1]

// Sprite sheet: 264×47px, each frame 44px wide.
// Frame 1 (x=44): standing T-Rex with eye open.
// Shift image left by 44px so that frame sits at origin in a 44×47 viewBox.
const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 48 48" role="img" aria-label="dis-connect">
  <rect width="48" height="48" rx="9" fill="#f7f7f7"/>
  <image xlink:href="${dataUri}" x="-42" y="0.5" width="264" height="47" image-rendering="pixelated"/>
</svg>
`

writeFileSync(join(root, 'public/favicon.svg'), svg)
console.log('favicon.svg written')
