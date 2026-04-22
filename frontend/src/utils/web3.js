import { Wallet, ethers } from 'ethers'

/**
 * 从母钱包助记词生成子钱包
 * @param {string} mnemonic - 母钱包助记词
 * @param {number} index - 子钱包索引（从0开始）
 * @returns {Object} 子钱包信息
 */
export function generateSubWallet(mnemonic, index = 0) {
  // 使用 BIP44 路径: m/44'/60'/0'/0/index
  const path = `m/44'/60'/0'/0/${index}`
  
  // 从助记词生成 HD 钱包
  const hdNode = ethers.utils.HDNode.fromMnemonic(mnemonic)
  const childNode = hdNode.derivePath(path)
  
  // 创建钱包实例
  const wallet = new Wallet(childNode.privateKey)
  
  return {
    address: wallet.address,
    privateKey: childNode.privateKey,
    publicKey: childNode.publicKey,
    path: path,
    index: index
  }
}

/**
 * 生成随机助记词（用于创建新的母钱包）
 * @returns {string} 助记词
 */
export function generateMnemonic() {
  return ethers.utils.entropyToMnemonic(ethers.utils.randomBytes(16))
}

/**
 * 验证助记词是否有效
 * @param {string} mnemonic - 助记词
 * @returns {boolean} 是否有效
 */
export function validateMnemonic(mnemonic) {
  return ethers.utils.isValidMnemonic(mnemonic)
}

/**
 * 从私钥导入钱包
 * @param {string} privateKey - 私钥
 * @returns {Object} 钱包信息
 */
export function importWalletFromPrivateKey(privateKey) {
  const wallet = new Wallet(privateKey)
  
  return {
    address: wallet.address,
    privateKey: privateKey,
    publicKey: wallet.publicKey
  }
}

/**
 * 签名消息
 * @param {string} privateKey - 私钥
 * @param {string} message - 消息
 * @returns {Promise<string>} 签名
 */
export async function signMessageWithKey(privateKey, message) {
  const wallet = new Wallet(privateKey)
  return await wallet.signMessage(message)
}
