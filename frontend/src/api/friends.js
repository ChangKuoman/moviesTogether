import client from './client'

export function getFriends() {
  return client.get('/friends').then((res) => res.data)
}

export function getIncomingRequests() {
  return client.get('/friends/requests/incoming').then((res) => res.data)
}

export function getOutgoingRequests() {
  return client.get('/friends/requests/outgoing').then((res) => res.data)
}

export function sendFriendRequest(recipientName) {
  return client.post('/friends/requests', { recipient_name: recipientName }).then((res) => res.data)
}

export function acceptRequest(requestId) {
  return client.post(`/friends/requests/${requestId}/accept`).then((res) => res.data)
}

export function declineRequest(requestId) {
  return client.post(`/friends/requests/${requestId}/decline`).then((res) => res.data)
}
