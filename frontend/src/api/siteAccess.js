import client from './client'

export function verifySiteAccess(passphrase) {
  return client.post('/site-access', { passphrase }).then((res) => res.data)
}
