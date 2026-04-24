import { ref } from 'vue'

export const tabs = [
  { id: 'description', label: 'Product Description' },
  { id: 'process', label: 'Transaction Process' },
  { id: 'safety', label: 'Safety Tips' }
]

export const transactionSteps = [
  { title: 'Browse & Select', desc: 'Browse products and select the item you want to purchase' },
  { title: 'Contact Seller', desc: 'Contact the seller to confirm product details and availability' },
  { title: 'Make Payment', desc: 'Complete payment through our secure payment system' },
  { title: 'Receive Product', desc: 'Seller delivers the product, verify and confirm receipt' },
  { title: 'Leave Review', desc: 'Share your experience and rate the product' }
]

export const antiFraudTips = [
  'Always communicate through the platform to keep records of all conversations',
  'Never share your password or payment verification codes with anyone',
  'Verify the seller\'s reputation and reviews before making a purchase',
  'Use only the official payment methods provided by the platform',
  'Be cautious of deals that seem too good to be true',
  'Report any suspicious activity to our support team immediately',
  'Keep all transaction records and screenshots for future reference',
  'Do not click on external links sent by sellers outside the platform'
]

export function useProductDetail() {
  const showVideo = ref(false)
  const currentImageIndex = ref(0)
  const isFollowing = ref(false)
  const isFavorited = ref(false)
  const showContactModal = ref(false)
  const message = ref('')
  const activeTab = ref('description')

  const selectImage = (index) => {
    currentImageIndex.value = index
    showVideo.value = false
  }

  const nextImage = () => {
    // Will be implemented in component where product is available
  }

  const prevImage = () => {
    // Will be implemented in component where product is available
  }

  const handleFollow = () => { isFollowing.value = !isFollowing.value }
  const handleFavorite = () => { isFavorited.value = !isFavorited.value }

  return {
    showVideo,
    currentImageIndex,
    isFollowing,
    isFavorited,
    showContactModal,
    message,
    activeTab,
    selectImage,
    nextImage,
    prevImage,
    handleFollow,
    handleFavorite
  }
}
