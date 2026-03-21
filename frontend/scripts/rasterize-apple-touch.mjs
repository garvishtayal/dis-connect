import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { Resvg } from '@resvg/resvg-js'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const svgPath = join(root, 'public/favicon.svg')
const outPath = join(root, 'public/apple-touch-icon.png')

const svg = readFileSync(svgPath, 'utf8')
const resvg = new Resvg(svg, {
  fitTo: { mode: 'width', value: 180 },
})
const png = resvg.render().asPng()
writeFileSync(outPath, png)
