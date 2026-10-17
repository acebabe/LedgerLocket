// small helpers for demo localStorage usage

const KEY_TRIALS = 'vns:trials'
const KEY_USER = 'vns:user'

export function loadLocalTrials() {
  try {
    return JSON.parse(localStorage.getItem(KEY_TRIALS) || '[]')
  } catch {
    return []
  }
}

export function saveLocalTrials(trials = []) {
  try {
    localStorage.setItem(KEY_TRIALS, JSON.stringify(trials))
  } catch {}
}

export function addLocalTrial(t) {
  const list = loadLocalTrials()
  list.push(t)
  saveLocalTrials(list)
  return t
}

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem(KEY_USER) || 'null')
  } catch {
    return null
  }
}

export function setCurrentUser(user) {
  try {
    if (!user) {
      localStorage.removeItem(KEY_USER)
    } else {
      localStorage.setItem(KEY_USER, JSON.stringify(user))
    }
  } catch {}
}