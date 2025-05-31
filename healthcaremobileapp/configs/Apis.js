import axios from "axios"

const BASE_URL = 'http://127.0.0.1:8000/'

export const endpoints = {
    'medical-records': '/medical-records/',
    'record-detail': '/record-detail/',
    'online-chat': '/online-chat/',
}

export default axios.create({
    baseURL: BASE_URL
})