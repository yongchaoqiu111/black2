import { defineStore } from 'pinia'
import { ref } from 'vue'
import { productsApi } from '@/services/api'

export const useProductStore = defineStore('product', () => {
  const products = ref([])
  const currentProduct = ref(null)
  const loading = ref(false)

  // Fetch all products and cache them
  async function fetchProducts(params = {}) {
    loading.value = true
    try {
      const response = await productsApi.getAll(params)
      const rawProducts = response.data.products || []
      
      // Normalize data structure for frontend consistency
      products.value = rawProducts.map(p => ({
        ...p,
        id: p.product_id, // Alias for compatibility
        seller: p.seller_address || 'Unknown Seller',
        images: p.images ? (Array.isArray(p.images) ? p.images : [p.images]) : [],
        video: p.video_url || '',
        sales: p.sales_count || 0,
        rating: p.rating || 5.0,
        reviews: p.review_count || 0,
        tags: p.tags || [],
        features: p.features || []
      }))
      
      return products.value
    } catch (error) {
      console.error('Failed to fetch products:', error)
      return []
    } finally {
      loading.value = false
    }
  }

  // Get product by ID (from cache or API)
  async function getProductById(productId) {
    // Check if already in list
    const cached = products.value.find(p => p.product_id === productId)
    if (cached) {
      currentProduct.value = cached
      return cached
    }

    // If not, fetch details
    loading.value = true
    try {
      const response = await productsApi.getById(productId)
      const rawProduct = response.data.product
      
      // Normalize data structure
      const normalizedProduct = {
        ...rawProduct,
        id: rawProduct.product_id,
        seller: rawProduct.seller_address || 'Unknown Seller',
        images: rawProduct.images ? (Array.isArray(rawProduct.images) ? rawProduct.images : [rawProduct.images]) : [],
        video: rawProduct.video_url || '',
        sales: rawProduct.sales_count || 0,
        rating: rawProduct.rating || 5.0,
        reviews: rawProduct.review_count || 0,
        tags: rawProduct.tags || [],
        features: rawProduct.features || []
      }
      
      currentProduct.value = normalizedProduct
      return currentProduct.value
    } catch (error) {
      console.error('Failed to fetch product details:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  // Set current product manually (e.g., when clicking from list)
  function setCurrentProduct(product) {
    // Normalize data before setting
    const normalizedProduct = {
      ...product,
      id: product.product_id,
      seller: product.seller_address || 'Unknown Seller',
      images: product.images ? (Array.isArray(product.images) ? product.images : [product.images]) : [],
      video: product.video_url || '',
      sales: product.sales_count || 0,
      rating: product.rating || 5.0,
      reviews: product.review_count || 0,
      tags: product.tags || [],
      features: product.features || []
    }

    currentProduct.value = normalizedProduct
    // Also update in the list if it exists there
    const index = products.value.findIndex(p => p.product_id === normalizedProduct.product_id)
    if (index !== -1) {
      products.value[index] = normalizedProduct
    } else {
      products.value.push(normalizedProduct)
    }
  }

  return {
    products,
    currentProduct,
    loading,
    fetchProducts,
    getProductById,
    setCurrentProduct
  }
})
