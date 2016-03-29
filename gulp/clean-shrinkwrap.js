/**
 * Run this script to clean the npm-shrinkwrap.json file if it fills with
 * stray "resolved" and "from" items.
 *
 * $ npm run clean-shrinkwrap
 *
 * adapted from "shonkwrap"
 * https://github.com/skybet/shonkwrap/blob/master/shonkwrap
 */
import fs from 'fs';
import shrinkwrap from './npm-shrinkwrap.json';

function gitDep(rep) {
  return /^git/.test(rep);
}

function replacer(key, val) {
  if (!this.version) {
    return val;
  }
  if (key === 'from' && !gitDep(this.resolved)) {
    return undefined;
  }
  if (key === 'resolved' && !gitDep(val) && this.from !== val) {
    return undefined;
  }
  return val;
}

fs.writeFileSync(
  './npm-shrinkwrap.json',
  JSON.stringify(shrinkwrap, replacer, 2));
