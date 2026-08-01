import { cpSync, existsSync, rmSync } from 'node:fs'
import { resolve } from 'node:path'

const source = resolve(process.cwd(), '../frontend/src')
const destination = resolve(process.cwd(), 'shared-src')

if (!existsSync(source)) {
  throw new Error(`Shared frontend source not found: ${source}`)
}

rmSync(destination, { recursive: true, force: true })
cpSync(source, destination, { recursive: true })
