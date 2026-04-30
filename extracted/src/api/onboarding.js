import request from './request'

export function getOnboardingList(params) {
  return request.get('/onboarding/', { params })
}

export function createOnboarding(data) {
  return request.post('/onboarding/', data)
}

export function updateOnboarding(data) {
  return request.put(`/onboarding/${data.id}`, data)
}

export function deleteOnboarding(id) {
  return request.delete(`/onboarding/${id}`)
}
