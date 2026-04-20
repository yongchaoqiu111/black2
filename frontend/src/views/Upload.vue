<template>
  <div class="min-h-screen bg-gray-50 pb-8">
    <div class="max-w-5xl mx-auto px-4 md:px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{{ $t('upload.pageTitle') }}</h1>
        <p class="text-sm md:text-base text-gray-600">{{ $t('upload.pageSubtitle') }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Import Method Selection -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">0</span>
            {{ $t('upload.chooseImportMethod') }}
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Repository Import -->
            <button 
              type="button"
              @click="importType = 'repository'"
              :class="[
                'p-4 border-2 rounded-lg transition-all text-left',
                importType === 'repository' 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-blue-300'
              ]"
            >
              <i class="fa-solid fa-code-branch text-2xl mb-2" :class="importType === 'repository' ? 'text-blue-600' : 'text-gray-400'"></i>
              <h3 class="font-semibold text-gray-900 mb-1">{{ $t('upload.repository') }}</h3>
              <p class="text-xs text-gray-600">GitHub, GitLab, Bitbucket</p>
              <p class="text-xs text-blue-600 mt-2 font-medium">{{ $t('upload.bestForSoftware') }}</p>
            </button>

            <!-- Cloud Storage Import -->
            <button 
              type="button"
              @click="importType = 'cloud'"
              :class="[
                'p-4 border-2 rounded-lg transition-all text-left',
                importType === 'cloud' 
                  ? 'border-purple-500 bg-purple-50' 
                  : 'border-gray-200 hover:border-purple-300'
              ]"
            >
              <i class="fa-solid fa-cloud-upload-alt text-2xl mb-2" :class="importType === 'cloud' ? 'text-purple-600' : 'text-gray-400'"></i>
              <h3 class="font-semibold text-gray-900 mb-1">{{ $t('upload.cloudStorage') }}</h3>
              <p class="text-xs text-gray-600">Baidu, Google Drive, Dropbox</p>
              <p class="text-xs text-purple-600 mt-2 font-medium">{{ $t('upload.bestForEbooks') }}</p>
            </button>

            <!-- Manual Upload -->
            <button 
              type="button"
              @click="importType = 'manual'"
              :class="[
                'p-4 border-2 rounded-lg transition-all text-left',
                importType === 'manual' 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-200 hover:border-green-300'
              ]"
            >
              <i class="fa-solid fa-edit text-2xl mb-2" :class="importType === 'manual' ? 'text-green-600' : 'text-gray-400'"></i>
              <h3 class="font-semibold text-gray-900 mb-1">{{ $t('upload.manualUpload') }}</h3>
              <p class="text-xs text-gray-600">{{ $t('upload.fillAllDetails') }}</p>
              <p class="text-xs text-green-600 mt-2 font-medium">{{ $t('upload.bestForAllTypes') }}</p>
            </button>
          </div>
        </div>

        <!-- Import from Repository Section -->
        <div v-if="importType === 'repository'" class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">1</span>
            {{ $t('upload.importFromRepository') }}
          </h2>

          <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-code-branch text-blue-600 text-xl mt-1"></i>
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 mb-2">{{ $t('upload.repositoryImport') }}</h3>
                <p class="text-sm text-gray-600 mb-3">{{ $t('upload.autoFetchInfo') }}</p>
                
                <div class="space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-700 mb-1">{{ $t('upload.repositoryUrl') }}</label>
                    <div class="flex space-x-2">
                      <input 
                        type="url" 
                        v-model="repositoryUrl"
                        :placeholder="$t('upload.repositoryUrlPlaceholder')"
                        class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 text-sm"
                      />
                      <button 
                        type="button"
                        @click="importFromRepo"
                        :disabled="!repositoryUrl || importing"
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm whitespace-nowrap"
                      >
                        <i v-if="importing" class="fa-solid fa-spinner fa-spin"></i>
                        <span>{{ importing ? $t('upload.importing') : $t('upload.import') }}</span>
                      </button>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ $t('upload.supportedPlatforms') }}</p>
                  </div>

                  <!-- AI Smart Fill Hint -->
                  <div v-if="repositoryUrl" class="mt-3 p-3 bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg">
                    <div class="flex items-start space-x-2">
                      <i class="fa-solid fa-magic text-purple-600 mt-0.5"></i>
                      <div class="flex-1">
                        <p class="text-xs text-purple-900 font-semibold">🤖 AI 智能识别已就�?/p>
                        <p class="text-xs text-purple-700 mt-1">
                          系统将自动分析您的仓库，提取项目名称、描述、技术栈、License等信息并填充表单�?
                        </p>
                        <p class="text-xs text-purple-600 mt-2">
                          💡 提示：只需提供GitHub链接，其余交给我们！
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- Imported Data Preview -->
                  <div v-if="importedData" class="mt-3 p-3 bg-white rounded border border-blue-200">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-semibold text-green-600 flex items-center">
                        <i class="fa-solid fa-check-circle mr-1"></i>
                        {{ $t('upload.successfullyImported') }}
                      </span>
                      <button 
                        type="button"
                        @click="clearImportedData"
                        class="text-xs text-red-600 hover:text-red-700"
                      >
                        {{ $t('upload.clear') }}
                      </button>
                    </div>
                    <div class="space-y-1 text-xs text-gray-600">
                      <p><strong>{{ $t('upload.name') }}:</strong> {{ importedData.name }}</p>
                      <p><strong>{{ $t('upload.description') }}:</strong> {{ importedData.description }}</p>
                      <p><strong>{{ $t('upload.version') }}:</strong> {{ importedData.version }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Cloud Storage Import Section -->
        <div v-if="importType === 'cloud'" class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-purple-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">1</span>
            {{ $t('upload.productStorageLocation') }}
          </h2>

          <div class="space-y-4">
            <!-- Storage Type Selection -->
            <div class="p-4 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
              <div class="flex items-start space-x-3 mb-4">
                <i class="fa-solid fa-database text-purple-600 text-xl mt-1"></i>
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900 mb-2">{{ $t('upload.whereIsProductStored') }}</h3>
                  <p class="text-sm text-gray-600">{{ $t('upload.storageLocationDesc') }}</p>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <!-- Cloud Storage Providers -->
                <label class="relative cursor-pointer">
                  <input 
                    type="radio" 
                    v-model="storageType"
                    value="cloud-provider"
                    class="peer sr-only"
                  />
                  <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
                    <div class="flex items-center space-x-3 mb-2">
                      <i class="fa-solid fa-cloud text-purple-600 text-xl"></i>
                      <span class="font-semibold text-gray-900">{{ $t('upload.cloudStorageProvider') }}</span>
                    </div>
                    <p class="text-xs text-gray-600">{{ $t('upload.cloudProviders') }}</p>
                    <p class="text-xs text-green-600 mt-2 font-medium">{{ $t('upload.easyVerifyAccessible') }}</p>
                  </div>
                </label>

                <!-- Torrent/P2P -->
                <label class="relative cursor-pointer">
                  <input 
                    type="radio" 
                    v-model="storageType"
                    value="torrent"
                    class="peer sr-only"
                  />
                  <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
                    <div class="flex items-center space-x-3 mb-2">
                      <i class="fa-solid fa-magnet text-orange-600 text-xl"></i>
                      <span class="font-semibold text-gray-900">{{ $t('upload.torrentP2P') }}</span>
                    </div>
                    <p class="text-xs text-gray-600">磁力链接、种子文件、IPFS哈希</p>
                    <p class="text-xs text-yellow-600 mt-2 font-medium">�?需要种子验�?/p>
                  </div>
                </label>

                <!-- Self-hosted Server -->
                <label class="relative cursor-pointer">
                  <input 
                    type="radio" 
                    v-model="storageType"
                    value="self-hosted"
                    class="peer sr-only"
                  />
                  <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
                    <div class="flex items-center space-x-3 mb-2">
                      <i class="fa-solid fa-server text-blue-600 text-xl"></i>
                      <span class="font-semibold text-gray-900">自建服务�?/span>
                    </div>
                    <p class="text-xs text-gray-600">自己的服务器、VPS或托管服�?/p>
                    <p class="text-xs text-blue-600 mt-2 font-medium">�?完全控制且可自定�?/p>
                  </div>
                </label>

                <!-- Blockchain/IPFS -->
                <label class="relative cursor-pointer">
                  <input 
                    type="radio" 
                    v-model="storageType"
                    value="blockchain"
                    class="peer sr-only"
                  />
                  <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
                    <div class="flex items-center space-x-3 mb-2">
                      <i class="fa-solid fa-link text-indigo-600 text-xl"></i>
                      <span class="font-semibold text-gray-900">区块�?/ IPFS</span>
                    </div>
                    <p class="text-xs text-gray-600">IPFS、Arweave、Filecoin（去中心化）</p>
                    <p class="text-xs text-indigo-600 mt-2 font-medium">�?永久存储且防篡改</p>
                  </div>
                </label>
              </div>
            </div>

            <!-- Storage Details Based on Type -->
            <div v-if="storageType === 'cloud-provider'" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">云存储服务商</label>
                <select 
                  v-model="cloudProvider"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                >
                  <option value="baidu">百度网盘 (Baidu Netdisk)</option>
                  <option value="aliyun">阿里云盘 (Aliyun Drive)</option>
                  <option value="quark">夸克网盘 (Quark Drive)</option>
                  <option value="google">Google Drive</option>
                  <option value="dropbox">Dropbox</option>
                  <option value="onedrive">Microsoft OneDrive</option>
                  <option value="mega">MEGA</option>
                  <option value="other">Other Provider</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  分享链接 <span class="text-red-500">*</span>
                </label>
                <input 
                  type="url" 
                  v-model="storageLink"
                  :placeholder="getStorageLinkPlaceholder()"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Provide a public share link that buyers can access</p>
              </div>

              <div v-if="cloudProvider === 'baidu' || cloudProvider === 'aliyun' || cloudProvider === 'quark'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Access Code (if required)
                </label>
                <input 
                  type="text" 
                  v-model="accessCode"
                  placeholder="例如：abcd"
                  maxlength="10"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Extraction code for Chinese cloud drives</p>
              </div>

              <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-start space-x-2">
                  <i class="fa-solid fa-info-circle text-blue-600 mt-0.5"></i>
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-gray-900 mb-1">Verification Requirements</h4>
                    <ul class="text-xs text-gray-700 space-y-1 ml-4 list-disc">
                      <li>Link must be publicly accessible (no login required for preview)</li>
                      <li>File must remain available for at least 90 days</li>
                      <li>We will test the link during review process</li>
                      <li>Broken links will result in product removal</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Torrent/P2P Details -->
            <div v-if="storageType === 'torrent'" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Torrent Type <span class="text-red-500">*</span>
                </label>
                <select 
                  v-model="torrentType"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                >
                  <option value="magnet">Magnet Link</option>
                  <option value="torrent-file">.torrent File</option>
                  <option value="ipfs">IPFS Hash</option>
                </select>
              </div>

              <div v-if="torrentType === 'magnet'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Magnet Link <span class="text-red-500">*</span>
                </label>
                <textarea 
                  v-model="magnetLink"
                  required
                  rows="3"
                  placeholder="magnet:?xt=urn:btih:..."
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-mono text-xs"
                ></textarea>
              </div>

              <div v-if="torrentType === 'torrent-file'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Upload .torrent File <span class="text-red-500">*</span>
                </label>
                <label class="block w-full px-4 py-3 border-2 border-dashed border-purple-300 rounded-lg cursor-pointer hover:border-purple-500 hover:bg-purple-50 transition-all text-center">
                  <input 
                    type="file" 
                    accept=".torrent"
                    @change="handleTorrentUpload"
                    class="hidden"
                  />
                  <i class="fa-solid fa-cloud-upload-alt text-purple-600 text-2xl mb-2 block"></i>
                  <span class="text-sm text-gray-700">Click to upload .torrent file</span>
                  <p class="text-xs text-gray-500 mt-1">Max size: 1MB</p>
                </label>
                <div v-if="torrentFile" class="mt-2 p-2 bg-purple-50 border border-purple-200 rounded flex items-center justify-between">
                  <div class="flex items-center space-x-2">
                    <i class="fa-solid fa-file text-purple-600"></i>
                    <span class="text-xs text-gray-700">{{ torrentFile.name }}</span>
                  </div>
                  <button 
                    type="button"
                    @click="torrentFile = null"
                    class="text-red-600 hover:text-red-700"
                  >
                    <i class="fa-solid fa-times"></i>
                  </button>
                </div>
              </div>

              <div v-if="torrentType === 'ipfs'">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  IPFS Hash (CID) <span class="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  v-model="ipfsHash"
                  required
                  placeholder="QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-mono text-xs"
                />
              </div>

              <div class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div class="flex items-start space-x-2">
                  <i class="fa-solid fa-exclamation-triangle text-yellow-600 mt-0.5"></i>
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-gray-900 mb-1">Seed Verification Required</h4>
                    <ul class="text-xs text-gray-700 space-y-1 ml-4 list-disc">
                      <li>You must maintain active seeding for at least 30 days after sale</li>
                      <li>We will verify seed availability during review</li>
                      <li>Minimum 2 seeders recommended for reliability</li>
                      <li>Failure to seed may result in refund requests and penalties</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Self-hosted Server Details -->
            <div v-if="storageType === 'self-hosted'" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Download URL <span class="text-red-500">*</span>
                </label>
                <input 
                  type="url" 
                  v-model="downloadUrl"
                  required
                  placeholder="https://your-server.com/downloads/product.zip"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Direct download link (must be accessible without login)</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Backup Storage (optional but recommended)
                </label>
                <input 
                  type="url" 
                  v-model="backupUrl"
                  placeholder="https://backup-server.com/product.zip"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Provide a backup link in case primary server is down</p>
              </div>

              <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="flex items-start space-x-2">
                  <i class="fa-solid fa-shield-alt text-blue-600 mt-0.5"></i>
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-gray-900 mb-1">Server Requirements</h4>
                    <ul class="text-xs text-gray-700 space-y-1 ml-4 list-disc">
                      <li>Server must have 99% uptime guarantee</li>
                      <li>Download speed should be at least 1 MB/s</li>
                      <li>HTTPS encryption required for security</li>
                      <li>We recommend using CDN for better performance</li>
                      <li>Regular backups are your responsibility</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Blockchain/IPFS Details -->
            <div v-if="storageType === 'blockchain'" class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Network <span class="text-red-500">*</span>
                </label>
                <select 
                  v-model="blockchainNetwork"
                  required
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                >
                  <option value="ipfs">IPFS (InterPlanetary File System)</option>
                  <option value="arweave">Arweave</option>
                  <option value="filecoin">Filecoin</option>
                  <option value="storj">Storj</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Content Identifier (CID/Hash) <span class="text-red-500">*</span>
                </label>
                <input 
                  type="text" 
                  v-model="blockchainHash"
                  required
                  :placeholder="getBlockchainHashPlaceholder()"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-mono text-xs"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Gateway URL (optional)
                </label>
                <input 
                  type="url" 
                  v-model="gatewayUrl"
                  :placeholder="getGatewayUrlPlaceholder()"
                  class="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Public gateway URL for easier access</p>
              </div>

              <div class="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div class="flex items-start space-x-2">
                  <i class="fa-solid fa-check-circle text-green-600 mt-0.5"></i>
                  <div class="flex-1">
                    <h4 class="text-sm font-semibold text-gray-900 mb-1">Advantages of Decentralized Storage</h4>
                    <ul class="text-xs text-gray-700 space-y-1 ml-4 list-disc">
                      <li>Permanent storage - files cannot be deleted</li>
                      <li>Tamper-proof - content integrity guaranteed by cryptography</li>
                      <li>No single point of failure</li>
                      <li>Easy to verify with hash comparison</li>
                      <li>Recommended for high-value digital products</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- File Information Display -->
            <div v-if="storageLink || magnetLink || downloadUrl || blockchainHash" class="p-4 bg-white rounded-lg border border-purple-200">
              <div class="flex items-center justify-between mb-3">
                <h4 class="font-semibold text-gray-900 flex items-center">
                  <i class="fa-solid fa-file-alt text-purple-600 mr-2"></i>
                  Detected File Information
                </h4>
                <button 
                  type="button"
                  @click="verifyStorageLink"
                  :disabled="verifying"
                  class="px-3 py-1.5 bg-purple-600 text-white rounded-lg text-xs hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center space-x-1"
                >
                  <i v-if="verifying" class="fa-solid fa-spinner fa-spin"></i>
                  <i v-else class="fa-solid fa-check-double"></i>
                  <span>{{ verifying ? 'Verifying...' : 'Verify Now' }}</span>
                </button>
              </div>
              
              <div v-if="verificationStatus" class="space-y-2">
                <div :class="[
                  'p-3 rounded-lg',
                  verificationStatus.status === 'valid' ? 'bg-green-50 border border-green-200' :
                  verificationStatus.status === 'invalid' ? 'bg-red-50 border border-red-200' :
                  'bg-yellow-50 border border-yellow-200'
                ]">
                  <div class="flex items-start space-x-2">
                    <i :class="[
                      'mt-0.5',
                      verificationStatus.status === 'valid' ? 'fa-solid fa-check-circle text-green-600' :
                      verificationStatus.status === 'invalid' ? 'fa-solid fa-times-circle text-red-600' :
                      'fa-solid fa-exclamation-circle text-yellow-600'
                    ]"></i>
                    <div class="flex-1">
                      <p class="text-sm font-medium" :class="[
                        verificationStatus.status === 'valid' ? 'text-green-900' :
                        verificationStatus.status === 'invalid' ? 'text-red-900' :
                        'text-yellow-900'
                      ]">{{ verificationStatus.message }}</p>
                      <p v-if="verificationStatus.details" class="text-xs text-gray-600 mt-1">{{ verificationStatus.details }}</p>
                    </div>
                  </div>
                </div>

                <div v-if="verificationStatus.fileInfo" class="grid grid-cols-2 gap-2 text-xs">
                  <div class="p-2 bg-gray-50 rounded">
                    <span class="text-gray-600">File Name:</span>
                    <span class="font-medium text-gray-900 ml-1">{{ verificationStatus.fileInfo.name }}</span>
                  </div>
                  <div class="p-2 bg-gray-50 rounded">
                    <span class="text-gray-600">File Size:</span>
                    <span class="font-medium text-gray-900 ml-1">{{ verificationStatus.fileInfo.size }}</span>
                  </div>
                  <div class="p-2 bg-gray-50 rounded">
                    <span class="text-gray-600">File Type:</span>
                    <span class="font-medium text-gray-900 ml-1">{{ verificationStatus.fileInfo.type }}</span>
                  </div>
                  <div class="p-2 bg-gray-50 rounded">
                    <span class="text-gray-600">Last Modified:</span>
                    <span class="font-medium text-gray-900 ml-1">{{ verificationStatus.fileInfo.modified }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Basic Information -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">{{ importType === 'manual' ? '1' : '2' }}</span>
            Basic Information
          </h2>

          <!-- Smart Guide -->
          <div v-if="!form.name && !form.category" class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-200 rounded-lg">
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-lightbulb text-blue-600 text-xl mt-0.5"></i>
              <div class="flex-1">
                <h4 class="font-semibold text-blue-900 mb-2">💡 智能引导助手</h4>
                <p class="text-sm text-blue-800 mb-3">让我帮您快速完成表单填写：</p>
                <ul class="space-y-2 text-sm text-blue-700">
                  <li class="flex items-start">
                    <span class="mr-2">1️⃣</span>
                    <span><strong>提供GitHub链接</strong> - AI自动分析并填充所有信�?/span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">2️⃣</span>
                    <span><strong>或手动填�?/strong> - 我会根据您填的内容智能提示下一�?/span>
                  </li>
                  <li class="flex items-start">
                    <span class="mr-2">3️⃣</span>
                    <span><strong>AI审计发布</strong> - 系统自动验证并上架到AI市场</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Dynamic Progress Hint -->
          <div v-if="form.name || form.category" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-check-circle text-green-600"></i>
              <span class="text-sm text-green-800 font-medium">
                {{ getProgressHint() }}
              </span>
            </div>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Product Name <span class="text-red-500">*</span>
              </label>
              <input 
                type="text" 
                v-model="form.name"
                required
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                placeholder="{{ $t('upload.productNamePlaceholder') }}"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Category <span class="text-red-500">*</span>
                </label>
                <select 
                  v-model="form.category"
                  required
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                >
                  <option value="">Select a category</option>
                  <option value="short-video">Short Video</option>
                  <option value="article">Article</option>
                  <option value="software">Software & Tools</option>
                  <option value="web-app">Website/App Source Code</option>
                  <option value="ebooks">E-books</option>
                  <option value="courses">Learning Courses</option>
                  <option value="design">Design Resources</option>
                  <option value="services">Comprehensive Services</option>
                  <option value="ai-tools">AI Tools</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Delivery Type
                </label>
                <select 
                  v-model="form.deliveryType"
                  :disabled="!form.category"
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base disabled:bg-gray-100 disabled:cursor-not-allowed"
                >
                  <option value="">{{ form.category ? 'Select delivery type' : 'Please select a category first' }}</option>
                  <option 
                    v-for="option in deliveryTypeOptions" 
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <p v-if="form.category" class="text-xs text-gray-500 mt-1">
                  <i class="fa-solid fa-info-circle mr-1"></i>
                  Available options based on "{{ getCategoryLabel(form.category) }}" category
                </p>
              </div>
            </div>

            <!-- Software Purpose -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-3">
                Software Purpose / Use Case
              </label>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="traffic"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                    <i class="fa-solid fa-chart-line text-blue-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Traffic Generation</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="ai-tool"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-purple-500 peer-checked:bg-purple-50 hover:border-purple-300 transition-all">
                    <i class="fa-solid fa-robot text-purple-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">AI Tool</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="automation"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-orange-500 peer-checked:bg-orange-50 hover:border-orange-300 transition-all">
                    <i class="fa-solid fa-cogs text-orange-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Automation</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="marketing"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-red-500 peer-checked:bg-red-50 hover:border-red-300 transition-all">
                    <i class="fa-solid fa-bullhorn text-red-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Marketing</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="emotional"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-pink-500 peer-checked:bg-pink-50 hover:border-pink-300 transition-all">
                    <i class="fa-solid fa-heart text-pink-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Emotional Value</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="learning"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-green-500 peer-checked:bg-green-50 hover:border-green-300 transition-all">
                    <i class="fa-solid fa-graduation-cap text-green-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Learning & Growth</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="efficiency"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-teal-500 peer-checked:bg-teal-50 hover:border-teal-300 transition-all">
                    <i class="fa-solid fa-tachometer-alt text-teal-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Cost & Efficiency</span>
                  </div>
                </label>

                <label class="relative cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.purposes"
                    value="data"
                    class="peer sr-only"
                  />
                  <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-indigo-500 peer-checked:bg-indigo-50 hover:border-indigo-300 transition-all">
                    <i class="fa-solid fa-database text-indigo-600 text-xl mb-2 block"></i>
                    <span class="text-xs font-medium text-gray-700">Data & Analytics</span>
                  </div>
                </label>
              </div>
            </div>

            <!-- Emotional Value Explanation -->
            <div v-if="form.purposes.includes('emotional')" class="mt-6 p-6 bg-gradient-to-br from-pink-50 via-purple-50 to-indigo-50 border-2 border-pink-300 rounded-xl">
              <div class="flex items-start space-x-4 mb-4">
                <div class="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <i class="fa-solid fa-heart text-white text-xl"></i>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-bold text-gray-900 mb-2">🎯 Why Choose Emotional Value?</h3>
                  <p class="text-sm text-gray-700 mb-4">Transform your creativity into a sustainable business with our revolutionary subscription model.</p>
                </div>
              </div>

              <!-- Comparison Table -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <!-- Traditional Platforms -->
                <div class="bg-white/80 backdrop-blur rounded-lg p-4 border-2 border-red-200">
                  <div class="flex items-center space-x-2 mb-3">
                    <i class="fa-solid fa-times-circle text-red-500 text-xl"></i>
                    <h4 class="font-bold text-red-700">Traditional Social Platforms</h4>
                  </div>
                  <ul class="space-y-2 text-sm text-gray-700">
                    <li class="flex items-start">
                      <i class="fa-solid fa-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
                      <span><strong>Algorithm Anxiety:</strong> Constantly worry about views and engagement</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
                      <span><strong>Hard to Monetize:</strong> Millions of views but minimal income</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
                      <span><strong>Single-Screen Trap:</strong> Endless scrolling, no user choice</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
                      <span><strong>Unstable Income:</strong> Dependent on viral content</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-exclamation-triangle text-red-500 mr-2 mt-0.5"></i>
                      <span><strong>No Direct Connection:</strong> Fans can't directly support you</span>
                    </li>
                  </ul>
                </div>

                <!-- Our Platform -->
                <div class="bg-white/80 backdrop-blur rounded-lg p-4 border-2 border-green-200">
                  <div class="flex items-center space-x-2 mb-3">
                    <i class="fa-solid fa-check-circle text-green-500 text-xl"></i>
                    <h4 class="font-bold text-green-700">Our Platform + OpenClaw</h4>
                  </div>
                  <ul class="space-y-2 text-sm text-gray-700">
                    <li class="flex items-start">
                      <i class="fa-solid fa-check text-green-500 mr-2 mt-0.5"></i>
                      <span><strong>Product Card Model:</strong> Package creativity as subscription products</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-check text-green-500 mr-2 mt-0.5"></i>
                      <span><strong>Fair Revenue:</strong> You keep 80-90% of subscription fees</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-check text-green-500 mr-2 mt-0.5"></i>
                      <span><strong>Precise Delivery:</strong> Content pushed to fans' OpenClaw devices</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-check text-green-500 mr-2 mt-0.5"></i>
                      <span><strong>Stable Income:</strong> Predictable monthly recurring revenue</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fa-solid fa-check text-green-500 mr-2 mt-0.5"></i>
                      <span><strong>Direct Fan Support:</strong> Fans subscribe because they love you</span>
                    </li>
                  </ul>
                </div>
              </div>

              <!-- Key Benefits -->
              <div class="bg-white/90 backdrop-blur rounded-lg p-4 border border-pink-200">
                <h4 class="font-bold text-gray-900 mb-3 flex items-center">
                  <i class="fa-solid fa-lightbulb text-yellow-500 mr-2"></i>
                  How It Works:
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-pink-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-pink-600 font-bold">1</span>
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900">Create Content</p>
                      <p class="text-gray-600">Dance, sing, perform - your talent</p>
                    </div>
                  </div>
                  <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-purple-600 font-bold">2</span>
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900">Package as Product</p>
                      <p class="text-gray-600">Set price, frequency, quality</p>
                    </div>
                  </div>
                  <div class="flex items-start space-x-3">
                    <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span class="text-indigo-600 font-bold">3</span>
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900">Fans Subscribe</p>
                      <p class="text-gray-600">Auto-deliver to their OpenClaw</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Success Example -->
              <div class="mt-4 p-4 bg-gradient-to-r from-pink-100 to-purple-100 rounded-lg border border-pink-300">
                <div class="flex items-start space-x-3">
                  <i class="fa-solid fa-star text-yellow-500 text-xl mt-1"></i>
                  <div class="flex-1">
                    <p class="font-semibold text-gray-900 mb-1">Real Example:</p>
                    <p class="text-sm text-gray-700">
                      A dancer with <strong>5,000 subscribers</strong> at <strong>$5/month</strong> earns 
                      <strong class="text-pink-600">$25,000/month</strong> (¥180,000) - 
                      compared to <strong class="text-red-600">¥3,000/month</strong> on traditional platforms.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Delivery Standards -->
            <div class="mt-6 space-y-6">
              <h3 class="text-lg font-bold text-gray-900 flex items-center">
                <i class="fa-solid fa-shipping-fast text-blue-600 mr-2"></i>
                Delivery Standards
              </h3>

              <!-- Update Frequency -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">
                  Update Frequency <span class="text-red-500">*</span>
                </label>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <label class="relative cursor-pointer">
                    <input 
                      type="radio" 
                      v-model="form.updateFrequency"
                      value="1-3-days"
                      class="peer sr-only"
                      required
                    />
                    <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                      <i class="fa-solid fa-bolt text-blue-600 text-xl mb-2 block"></i>
                      <span class="text-xs font-medium text-gray-700">Every 1-3 Days</span>
                      <p class="text-xs text-gray-500 mt-1">High frequency</p>
                    </div>
                  </label>

                  <label class="relative cursor-pointer">
                    <input 
                      type="radio" 
                      v-model="form.updateFrequency"
                      value="4-7-days"
                      class="peer sr-only"
                    />
                    <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                      <i class="fa-solid fa-calendar-week text-green-600 text-xl mb-2 block"></i>
                      <span class="text-xs font-medium text-gray-700">Every 4-7 Days</span>
                      <p class="text-xs text-gray-500 mt-1">Weekly</p>
                    </div>
                  </label>

                  <label class="relative cursor-pointer">
                    <input 
                      type="radio" 
                      v-model="form.updateFrequency"
                      value="weekly"
                      class="peer sr-only"
                    />
                    <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                      <i class="fa-solid fa-calendar-alt text-purple-600 text-xl mb-2 block"></i>
                      <span class="text-xs font-medium text-gray-700">Weekly Fixed</span>
                      <p class="text-xs text-gray-500 mt-1">Same day each week</p>
                    </div>
                  </label>

                  <label class="relative cursor-pointer">
                    <input 
                      type="radio" 
                      v-model="form.updateFrequency"
                      value="monthly"
                      class="peer sr-only"
                    />
                    <div class="p-3 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                      <i class="fa-solid fa-calendar-month text-orange-600 text-xl mb-2 block"></i>
                      <span class="text-xs font-medium text-gray-700">Monthly</span>
                      <p class="text-xs text-gray-500 mt-1">Premium content</p>
                    </div>
                  </label>
                </div>
              </div>

              <!-- Delivery Method -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">
                  Delivery Method <span class="text-red-500">*</span>
                </label>
                <div class="space-y-3">
                  <!-- Level 1: API Direct -->
                  <label class="relative cursor-pointer block">
                    <input 
                      type="radio" 
                      v-model="form.deliveryChannel"
                      value="api-direct"
                      class="peer sr-only"
                      required
                    />
                    <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-green-500 peer-checked:bg-green-50 hover:border-green-300 transition-all">
                      <div class="flex items-start space-x-3">
                        <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span class="text-green-600 font-bold">L1</span>
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center justify-between mb-1">
                            <h4 class="font-semibold text-gray-900">API Direct Push to OpenClaw</h4>
                            <span class="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">Recommended</span>
                          </div>
                          <p class="text-sm text-gray-600 mb-2">Direct API integration for automatic content delivery to subscribers' OpenClaw devices</p>
                          <ul class="text-xs text-gray-500 space-y-1 ml-4 list-disc">
                            <li>�?Instant delivery</li>
                            <li>�?Real-time notifications</li>
                            <li>�?Best user experience</li>
                            <li>�?Higher subscriber retention</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </label>

                  <!-- Level 2: AI Agent -->
                  <label class="relative cursor-pointer block">
                    <input 
                      type="radio" 
                      v-model="form.deliveryChannel"
                      value="ai-agent"
                      class="peer sr-only"
                    />
                    <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-blue-500 peer-checked:bg-blue-50 hover:border-blue-300 transition-all">
                      <div class="flex items-start space-x-3">
                        <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span class="text-blue-600 font-bold">L2</span>
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center justify-between mb-1">
                            <h4 class="font-semibold text-gray-900">AI Smart Agent Integration</h4>
                            <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">Popular</span>
                          </div>
                          <p class="text-sm text-gray-600 mb-2">AI agent handles content packaging, upload, and delivery automation</p>
                          <ul class="text-xs text-gray-500 space-y-1 ml-4 list-disc">
                            <li>�?AI handles technical work</li>
                            <li>�?Automatic API creation</li>
                            <li>�?You just create content</li>
                            <li>⚠️ Small service fee applies</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </label>

                  <!-- Level 3: Cloud Storage + AI Mentor -->
                  <label class="relative cursor-pointer block">
                    <input 
                      type="radio" 
                      v-model="form.deliveryChannel"
                      value="cloud-storage"
                      class="peer sr-only"
                    />
                    <div class="p-4 border-2 border-gray-200 rounded-lg peer-checked:border-orange-500 peer-checked:bg-orange-50 hover:border-orange-300 transition-all">
                      <div class="flex items-start space-x-3">
                        <div class="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span class="text-orange-600 font-bold">L3</span>
                        </div>
                        <div class="flex-1">
                          <div class="flex items-center justify-between mb-1">
                            <h4 class="font-semibold text-gray-900">Cloud Storage + AI Mentor Service</h4>
                            <span class="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full font-medium">Basic</span>
                          </div>
                          <p class="text-sm text-gray-600 mb-2">Regular updates to cloud storage with AI mentor guidance for API integration</p>
                          <ul class="text-xs text-gray-500 space-y-1 ml-4 list-disc">
                            <li>�?Upload to Baidu/Google Drive</li>
                            <li>�?AI mentor helps setup</li>
                            <li>�?Gradual migration to API</li>
                            <li>⚠️ Manual steps required initially</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </label>
                </div>

                <!-- AI Market Notice -->
                <div v-if="form.deliveryChannel === 'ai-agent' || form.deliveryChannel === 'cloud-storage'" class="mt-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-300 rounded-lg">
                  <div class="flex items-start space-x-3">
                    <i class="fa-solid fa-robot text-indigo-600 text-xl mt-1"></i>
                    <div class="flex-1">
                      <h4 class="font-semibold text-indigo-900 mb-2">🤖 AI Agent Marketplace</h4>
                      <p class="text-sm text-indigo-800 mb-2">
                        Your delivery task will be posted to the AI Agent Marketplace. AI agents will compete to serve you:
                      </p>
                      <ul class="text-xs text-indigo-700 space-y-1 ml-4 list-disc">
                        <li><strong>You focus on:</strong> Creating amazing content (videos, articles, etc.)</li>
                        <li><strong>AI agents handle:</strong> Packaging, uploading, API creation, delivery automation</li>
                        <li><strong>Benefits:</strong> Lower cost, faster setup, continuous optimization</li>
                        <li><strong>Process:</strong> Post task �?AI bids �?Select best offer �?AI completes setup</li>
                      </ul>
                      <div class="mt-3 p-3 bg-white/80 rounded-lg border border-indigo-200">
                        <p class="text-xs text-indigo-900">
                          <i class="fa-solid fa-lightbulb text-yellow-500 mr-1"></i>
                          <strong>Example:</strong> A dancer posts weekly videos �?AI agent packages them �?Creates API �?Pushes to 5,000 subscribers' OpenClaw devices automatically
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>


            <!-- Programming Language -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Programming Language
              </label>
              <select 
                v-model="form.language"
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
              >
                <option value="">Select language</option>
                <option value="javascript">JavaScript / TypeScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="php">PHP</option>
                <option value="csharp">C# / .NET</option>
                <option value="cpp">C / C++</option>
                <option value="go">Go</option>
                <option value="ruby">Ruby</option>
                <option value="swift">Swift</option>
                <option value="kotlin">Kotlin</option>
                <option value="other">Other</option>
              </select>
            </div>

            <!-- Open Source & Support Options -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.isOpenSource"
                    class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Open Source</span>
                </label>
              </div>

              <div>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.supportNegotiation"
                    class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Support Price Negotiation</span>
                </label>
              </div>

              <div>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.supportCustomization"
                    class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Support Custom Development</span>
                </label>
              </div>

              <div>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.longTermSupport"
                    class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Long-term Maintenance</span>
                </label>
              </div>

              <div>
                <label class="flex items-center space-x-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    v-model="form.acceptEscrow"
                    class="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Accept Platform Escrow</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Media Upload -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">2</span>
            Product Media
          </h2>

          <!-- Images Upload -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-3">
              Product Images <span class="text-red-500">*</span>
              <span class="text-gray-500 font-normal ml-2 text-xs md:text-sm">(Up to 5 images)</span>
            </label>
            
            <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3 md:gap-4 mb-4">
              <!-- Existing Images Preview -->
              <div 
                v-for="(img, index) in form.images" 
                :key="index"
                class="relative aspect-square rounded-lg overflow-hidden border-2 border-gray-200 group"
              >
                <img :src="img" class="w-full h-full object-cover" />
                <button 
                  type="button"
                  @click="removeImage(index)"
                  class="absolute top-1 right-1 md:top-2 md:right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                >
                  <svg class="w-3 h-3 md:w-4 md:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Upload Button -->
              <label 
                v-if="form.images.length < 5"
                class="aspect-square rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all"
              >
                <input 
                  type="file" 
                  accept="image/*"
                  multiple
                  @change="handleImageUpload"
                  class="hidden"
                />
                <svg class="w-6 h-6 md:w-8 md:h-8 text-gray-400 mb-1 md:mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span class="text-xs text-gray-500">Add</span>
              </label>
            </div>

            <p class="text-xs text-gray-500">Supported: JPG, PNG, GIF. Max 5MB per image.</p>
          </div>

          <!-- Video Upload -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-3">
              Product Video
              <span class="text-gray-500 font-normal ml-2 text-xs md:text-sm">(Optional)</span>
            </label>
            
            <div v-if="!form.video" class="border-2 border-dashed border-gray-300 rounded-lg p-6 md:p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition-all cursor-pointer">
              <label class="cursor-pointer block">
                <input 
                  type="file" 
                  accept="video/*"
                  @change="handleVideoUpload"
                  class="hidden"
                />
                <svg class="w-10 h-10 md:w-12 md:h-12 text-gray-400 mx-auto mb-2 md:mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <p class="text-sm text-gray-600 mb-1">Click to upload video</p>
                <p class="text-xs text-gray-500">MP4, WebM. Max 50MB</p>
              </label>
            </div>

            <div v-else class="relative rounded-lg overflow-hidden border-2 border-gray-200">
              <video :src="form.video" controls class="w-full aspect-video"></video>
              <button 
                type="button"
                @click="removeVideo"
                class="absolute top-2 right-2 md:top-3 md:right-3 w-7 h-7 md:w-8 md:h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-md"
              >
                <svg class="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Product Description -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">3</span>
            Product Description
          </h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Short Description <span class="text-red-500">*</span>
              </label>
              <textarea 
                v-model="form.shortDescription"
                required
                maxlength="200"
                rows="3"
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-none text-sm md:text-base"
                placeholder="{{ $t('upload.shortDescPlaceholder') }}"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">{{ form.shortDescription.length }}/200 characters</p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Detailed Description <span class="text-red-500">*</span>
              </label>
              <textarea 
                v-model="form.description"
                required
                rows="6"
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-y text-sm md:text-base"
                placeholder="{{ $t('upload.descriptionPlaceholder') }}"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Key Features
                <span class="text-gray-500 font-normal ml-2 text-xs md:text-sm">(One per line)</span>
              </label>
              <textarea 
                v-model="form.featuresText"
                rows="4"
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all resize-y text-sm md:text-base"
                placeholder="{{ $t('upload.featuresPlaceholder') }}"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Additional Info -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">4</span>
            Additional Information
          </h2>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Tags</label>
              <input 
                type="text" 
                v-model="form.tagsText"
                class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                placeholder="{{ $t('upload.tagsPlaceholder') }}"
              />
              <p class="text-xs text-gray-500 mt-1">Separate tags with commas</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Version</label>
                <input 
                  type="text" 
                  v-model="form.version"
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                  placeholder="{{ $t('upload.versionPlaceholder') }}"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">License Type</label>
                <select 
                  v-model="form.license"
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                >
                  <option value="lifetime">Lifetime License</option>
                  <option value="subscription">Subscription</option>
                  <option value="one-year">One Year License</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Content Verification -->
        <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg shadow-sm p-4 md:p-6 border-2 border-indigo-200">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">🤖</span>
            AI Content Verification
          </h2>

          <div class="space-y-4">
            <!-- Verification Info -->
            <div class="p-4 bg-white rounded-lg border border-indigo-200">
              <div class="flex items-start space-x-3">
                <i class="fa-solid fa-shield-alt text-indigo-600 text-xl mt-1"></i>
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900 mb-2">Automated Content Authenticity Check</h3>
                  <p class="text-sm text-gray-600 mb-3">Our AI system will verify your product's authenticity, detect potential issues, and ensure compliance with platform policies.</p>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-700">
                    <div class="flex items-center space-x-2">
                      <i class="fa-solid fa-check-circle text-green-600"></i>
                      <span>Detect fake or misleading content</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <i class="fa-solid fa-check-circle text-green-600"></i>
                      <span>Verify copyright compliance</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <i class="fa-solid fa-check-circle text-green-600"></i>
                      <span>Check for prohibited keywords</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <i class="fa-solid fa-check-circle text-green-600"></i>
                      <span>Validate category appropriateness</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Run Verification Button -->
            <button 
              type="button"
              @click="runAIVerification"
              :disabled="!canVerify || verifying"
              class="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-md"
            >
              <i v-if="verifying" class="fa-solid fa-spinner fa-spin"></i>
              <i v-else class="fa-solid fa-robot"></i>
              <span>{{ verifying ? 'AI Verifying...' : (verificationResult ? 'Re-run AI Verification' : 'Run AI Verification') }}</span>
            </button>

            <!-- Verification Result -->
            <div v-if="verificationResult" class="space-y-3">
              <!-- Status Banner -->
              <div 
                :class="[
                  'p-4 rounded-lg border-2',
                  verificationResult.status === 'approved' 
                    ? 'bg-green-50 border-green-300' 
                    : 'bg-red-50 border-red-300'
                ]"
              >
                <div class="flex items-center space-x-3">
                  <i 
                    :class="[
                      'text-2xl',
                      verificationResult.status === 'approved' ? 'fa-solid fa-check-circle text-green-600' : 'fa-solid fa-times-circle text-red-600'
                    ]"
                  ></i>
                  <div class="flex-1">
                    <h4 class="font-bold" :class="verificationResult.status === 'approved' ? 'text-green-900' : 'text-red-900'">
                      {{ verificationResult.status === 'approved' ? '�?Verification Passed!' : '�?Verification Failed' }}
                    </h4>
                    <p class="text-xs mt-1" :class="verificationResult.status === 'approved' ? 'text-green-700' : 'text-red-700'">
                      Confidence: {{ (verificationResult.confidence * 100).toFixed(1) }}% | 
                      Model: {{ verificationResult.aiModel }} | 
                      Time: {{ verificationResult.processingTime }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Issues List -->
              <div v-if="verificationResult.issues.length > 0" class="bg-white rounded-lg border border-gray-200 p-4">
                <h4 class="font-semibold text-gray-900 mb-3 flex items-center">
                  <i class="fa-solid fa-exclamation-triangle text-yellow-600 mr-2"></i>
                  Issues Found ({{ verificationResult.issues.length }})
                </h4>
                <div class="space-y-2">
                  <div 
                    v-for="(issue, index) in verificationResult.issues" 
                    :key="index"
                    :class="[
                      'p-3 rounded-lg border-l-4',
                      issue.severity === 'critical' ? 'bg-red-50 border-red-500' :
                      issue.severity === 'high' ? 'bg-orange-50 border-orange-500' :
                      issue.severity === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                      'bg-blue-50 border-blue-500'
                    ]"
                  >
                    <div class="flex items-start space-x-2">
                      <i 
                        :class="[
                          'mt-0.5',
                          issue.type === 'error' ? 'fa-solid fa-times-circle text-red-600' : 'fa-solid fa-info-circle text-blue-600'
                        ]"
                      ></i>
                      <div class="flex-1">
                        <p class="text-sm text-gray-900">{{ issue.message }}</p>
                        <p class="text-xs text-gray-500 mt-1">Field: {{ issue.field }} | Severity: {{ issue.severity }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recommendations -->
              <div v-if="verificationResult.recommendations.length > 0" class="bg-white rounded-lg border border-gray-200 p-4">
                <h4 class="font-semibold text-gray-900 mb-3 flex items-center">
                  <i class="fa-solid fa-lightbulb text-yellow-600 mr-2"></i>
                  AI Recommendations
                </h4>
                <ul class="space-y-2">
                  <li 
                    v-for="(rec, index) in verificationResult.recommendations" 
                    :key="index"
                    class="flex items-start space-x-2 text-sm text-gray-700"
                  >
                    <i class="fa-solid fa-arrow-right text-indigo-600 mt-1"></i>
                    <span>{{ rec }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Not Verified Warning -->
            <div v-if="!verificationResult && canVerify" class="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div class="flex items-start space-x-2">
                <i class="fa-solid fa-exclamation-circle text-yellow-600 mt-0.5"></i>
                <div class="flex-1">
                  <p class="text-sm text-yellow-900 font-medium">Verification Recommended</p>
                  <p class="text-xs text-yellow-700 mt-1">Running AI verification helps improve trust and reduces rejection risk. Products that pass verification get priority placement.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Expected Selling Price -->
        <div class="bg-white rounded-lg shadow-sm p-4 md:p-6">
          <h2 class="text-lg md:text-xl font-bold text-gray-900 mb-4 md:mb-6 flex items-center">
            <span class="w-7 h-7 md:w-8 md:h-8 bg-yellow-500 text-white rounded-full flex items-center justify-center mr-3 text-xs md:text-sm">5</span>
            Expected Selling Price
          </h2>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Your Expected Price (USDT)
            </label>
            <input 
              type="number" 
              v-model="form.price"
              min="0"
              step="0.01"
              class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
              placeholder="Enter your expected selling price"
            />
          </div>

          <!-- AI Audit Market Notice -->
          <div class="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg">
            <div class="flex items-start space-x-3">
              <i class="fa-solid fa-robot text-blue-600 text-xl mt-1"></i>
              <div class="flex-1">
                <h4 class="font-semibold text-blue-900 mb-2">🤖 AI Audit Marketplace</h4>
                <p class="text-sm text-blue-800">
                  Your product will first enter the <strong>AI Audit Marketplace</strong>, where professional AI agents will evaluate it and provide you with a <strong>final recommended selling price</strong> to help you sell faster.
                </p>
                <ul class="text-xs text-blue-700 mt-2 space-y-1 ml-4 list-disc">
                  <li>�?AI analyzes market demand and competitor pricing</li>
                  <li>�?Provides optimal pricing strategy</li>
                  <li>�?Increases your sales conversion rate</li>
                  <li>�?You can accept or adjust the AI's recommendation</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Notification Contact -->
          <div class="mt-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Contact for Audit Results <span class="text-red-500">*</span>
            </label>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <input 
                  type="email" 
                  v-model="form.notificationEmail"
                  placeholder="Email address"
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                />
              </div>
              <div>
                <input 
                  type="tel" 
                  v-model="form.notificationPhone"
                  placeholder="Or phone number"
                  class="w-full px-3 md:px-4 py-2.5 md:py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-sm md:text-base"
                />
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              <i class="fa-solid fa-info-circle mr-1"></i>
              We'll send the AI audit results and pricing recommendations to your email or phone
            </p>
          </div>
        </div>

        <!-- Submit Buttons -->
        <div class="space-y-4">
          <!-- 流程说明卡片 -->
          <div v-if="!verificationResult" class="p-5 bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-300 rounded-xl">
            <h4 class="font-bold text-purple-900 mb-3 flex items-center">
              <i class="fa-solid fa-info-circle text-purple-600 mr-2"></i>
              发布流程说明
            </h4>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div class="bg-white rounded-lg p-3 text-center">
                <div class="text-2xl mb-1">📤</div>
                <div class="font-semibold text-gray-900">发布出售</div>
                <div class="text-xs text-gray-600 mt-1">提交到AI市场</div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center">
                <div class="text-2xl mb-1">🤖</div>
                <div class="font-semibold text-gray-900">AI竞标审核</div>
                <div class="text-xs text-gray-600 mt-1">AI评估定价</div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center">
                <div class="text-2xl mb-1">📋</div>
                <div class="font-semibold text-gray-900">查看审计报告</div>
                <div class="text-xs text-gray-600 mt-1">确认最终价�?/div>
              </div>
              <div class="bg-white rounded-lg p-3 text-center">
                <div class="text-2xl mb-1">💰</div>
                <div class="font-semibold text-gray-900">支付上架</div>
                <div class="text-xs text-gray-600 mt-1">7天销售期</div>
              </div>
            </div>
            <div class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-xs text-yellow-800">
              <strong>💡 提示�?/strong>点击"先运行AI审计"后，您的商品将发布到AI市场，AI代理会竞标审核并给出最优价格建议�?天内售出则结算给AI，未售出则全额退款�?
            </div>
          </div>

          <div class="flex flex-col sm:flex-row gap-3 md:gap-4">
            <button 
              type="button"
              @click="handlePublishClick"
              :disabled="!canPublish"
              class="flex-1 py-3 md:py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-bold text-base md:text-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <i class="fa-solid fa-rocket mr-2"></i>
              {{ !verificationResult ? '先运行AI审计' : (auditPassed ? '发布到AI审计市场 ($1.49)' : '先修复问�?) }}
            </button>
            
            <button 
              type="button"
              @click="handleSaveDraft"
              class="px-6 md:px-8 py-3 md:py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors text-base md:text-lg"
            >
              Save as Draft
            </button>
          </div>
        </div>

        <!-- Audit Required Notice -->
        <div v-if="!verificationResult && canVerify" class="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-lg">
          <div class="flex items-start space-x-3">
            <i class="fa-solid fa-info-circle text-yellow-600 text-xl mt-1"></i>
            <div class="flex-1">
              <h4 class="font-semibold text-yellow-900 mb-1">AI Audit Required</h4>
              <p class="text-sm text-yellow-800 mb-2">Before publishing, our AI will audit your product to ensure quality and provide optimization suggestions.</p>
              <ul class="text-xs text-yellow-700 space-y-1 ml-4 list-disc">
                <li>�?Free audit - see the report first</li>
                <li>�?Only pay $1.49 if you're satisfied</li>
                <li>�?Get professional optimization suggestions</li>
                <li>�?Increase your sales potential by 140%</li>
              </ul>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- Publish Flow Modal -->
    <div v-if="showPublishModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="showPublishModal = false"></div>
      <div class="relative bg-white rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 text-white">
          <h3 class="text-2xl font-bold mb-2"> 发布到AI市场</h3>
          <p class="text-purple-100">确认后将启动完整的AI审核与销售流�?/p>
        </div>

        <!-- Flow Steps -->
        <div class="p-6 space-y-4">
          <!-- Step 1 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">📤</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第一步：发布出售</h4>
              <p class="text-sm text-gray-600 mt-1">您的商品将提交到AI市场，进入审核队�?/p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 2 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">🤖</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第二步：AI竞标审核</h4>
              <p class="text-sm text-gray-600 mt-1">多个AI代理竞标审核您的商品，评估质量、市场需求和竞争情况</p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 3 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">📋</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第三步：查看审计文档</h4>
              <p class="text-sm text-gray-600 mt-1">AI提供详细的审计报告，包括质量评分、优化建议和市场分析</p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 4 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">💰</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第四步：最终敲定贩卖价�?/h4>
              <p class="text-sm text-gray-600 mt-1">根据AI建议，您确认最终销售价格，可接受或调整</p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 5 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">💳</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第五步：支付费用给平�?/h4>
              <p class="text-sm text-gray-600 mt-1">支付上架费用�?1.49），商品正式上架到市�?/p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 6 -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
              <span class="text-2xl">🏪</span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第六步：上架出售�?天销售期�?/h4>
              <p class="text-sm text-gray-600 mt-1">商品在市场展�?天，等待买家购买</p>
            </div>
          </div>

          <!-- Arrow -->
          <div class="flex justify-center">
            <i class="fa-solid fa-arrow-down text-gray-300 text-2xl"></i>
          </div>

          <!-- Step 7 - Final -->
          <div class="flex items-start space-x-4">
            <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span class="text-2xl">�?/span>
            </div>
            <div class="flex-1">
              <h4 class="font-bold text-gray-900 text-lg">第七步：销售结�?/h4>
              <div class="mt-2 space-y-2">
                <div class="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                  <p class="text-sm text-green-900 font-semibold">�?7天内售出</p>
                  <p class="text-xs text-green-700 mt-1">平台自动结算佣金给AI代理，交易完�?/p>
                </div>
                <div class="p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <p class="text-sm text-blue-900 font-semibold">�?7天未售出</p>
                  <p class="text-xs text-blue-700 mt-1">全额退款给用户，商品下�?/p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Warning -->
        <div class="px-6 pb-4">
          <div class="p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
            <div class="flex items-start space-x-2">
              <i class="fa-solid fa-exclamation-triangle text-yellow-600 mt-1"></i>
              <div class="flex-1">
                <p class="text-sm text-yellow-900 font-semibold">重要提示</p>
                <ul class="text-xs text-yellow-800 mt-1 space-y-1 ml-4 list-disc">
                  <li>发布后商品将进入AI审核流程，无法撤�?/li>
                  <li>审核通过后需支付$1.49上架�?/li>
                  <li>7天销售期内售出则结算给AI，未售出则全额退�?/li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="px-6 pb-6 flex gap-3">
          <button 
            @click="showPublishModal = false"
            class="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            取消
          </button>
          <button 
            @click="confirmPublish"
            class="flex-1 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-bold hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg flex items-center justify-center space-x-2"
          >
            <i class="fa-solid fa-check"></i>
            <span>确认发布</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Modal -->
    <div v-if="showPaymentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/60" @click="showPaymentModal = false"></div>
      <div class="relative bg-white rounded-lg max-w-lg w-full p-6 md:p-8 shadow-2xl">
        <!-- Header -->
        <div class="text-center mb-6">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fa-solid fa-credit-card text-white text-2xl"></i>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Complete Your Listing</h3>
          <p class="text-gray-600">Pay once, sell forever</p>
        </div>

        <!-- Product Summary -->
        <div class="bg-gray-50 rounded-lg p-4 mb-6">
          <h4 class="font-semibold text-gray-900 mb-2">{{ form.name }}</h4>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span class="text-gray-600">Category:</span>
              <span class="ml-1 font-medium">{{ getCategoryLabel(form.category) }}</span>
            </div>
            <div>
              <span class="text-gray-600">Price:</span>
              <span class="ml-1 font-medium">${{ form.price }} USDT</span>
            </div>
          </div>
        </div>

        <!-- Audit Results Summary -->
        <div v-if="verificationResult" class="mb-6">
          <div :class="[
            'p-4 rounded-lg border-2 mb-4',
            verificationResult.status === 'approved' ? 'bg-green-50 border-green-300' : 'bg-yellow-50 border-yellow-300'
          ]">
            <div class="flex items-center space-x-2 mb-2">
              <i :class="[
                'text-xl',
                verificationResult.status === 'approved' ? 'fa-solid fa-check-circle text-green-600' : 'fa-solid fa-exclamation-triangle text-yellow-600'
              ]"></i>
              <span class="font-semibold" :class="verificationResult.status === 'approved' ? 'text-green-900' : 'text-yellow-900'">
                AI Audit {{ verificationResult.status === 'approved' ? 'Passed' : 'Completed with Suggestions' }}
              </span>
            </div>
            <p class="text-xs text-gray-700">Score: {{ (verificationResult.confidence * 100).toFixed(0) }}/100</p>
            <p v-if="verificationResult.issues.length > 0" class="text-xs text-gray-600 mt-1">
              {{ verificationResult.issues.length }} suggestion(s) provided
            </p>
          </div>
        </div>

        <!-- Pricing Breakdown -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-6">
          <h4 class="font-semibold text-gray-900 mb-3">What You Get:</h4>
          <ul class="space-y-2 text-sm text-gray-700">
            <li class="flex items-start space-x-2">
              <i class="fa-solid fa-check text-green-600 mt-1"></i>
              <span>AI-certified product listing</span>
            </li>
            <li class="flex items-start space-x-2">
              <i class="fa-solid fa-check text-green-600 mt-1"></i>
              <span>Permanent sales rights (no recurring fees)</span>
            </li>
            <li class="flex items-start space-x-2">
              <i class="fa-solid fa-check text-green-600 mt-1"></i>
              <span>Professional audit report for buyers</span>
            </li>
            <li class="flex items-start space-x-2">
              <i class="fa-solid fa-check text-green-600 mt-1"></i>
              <span>Increased trust and conversion rate</span>
            </li>
            <li class="flex items-start space-x-2">
              <i class="fa-solid fa-check text-green-600 mt-1"></i>
              <span>Platform promotion and exposure</span>
            </li>
          </ul>
          
          <div class="mt-4 pt-4 border-t border-blue-200">
            <div class="flex items-center justify-between">
              <span class="text-lg font-bold text-gray-900">One-time Fee:</span>
              <span class="text-2xl font-bold text-blue-600">$1.49</span>
            </div>
            <p class="text-xs text-gray-600 mt-1">�?1.49 USDT</p>
          </div>
        </div>

        <!-- Payment Methods -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">Select Payment Method</label>
          <div class="space-y-2">
            <label class="flex items-center p-3 border-2 border-blue-500 bg-blue-50 rounded-lg cursor-pointer">
              <input type="radio" v-model="paymentMethod" value="usdt" class="mr-3" checked />
              <div class="flex-1">
                <div class="font-medium text-gray-900">USDT (TRC20)</div>
                <div class="text-xs text-gray-600">Recommended - Fast & Low Fee</div>
              </div>
              <i class="fa-brands fa-bitcoin text-blue-600 text-xl"></i>
            </label>
            
            <label class="flex items-center p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-gray-300">
              <input type="radio" v-model="paymentMethod" value="btc" class="mr-3" />
              <div class="flex-1">
                <div class="font-medium text-gray-900">Bitcoin (BTC)</div>
                <div class="text-xs text-gray-600">Higher fee, slower confirmation</div>
              </div>
              <i class="fa-brands fa-bitcoin text-orange-600 text-xl"></i>
            </label>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3">
          <button 
            @click="showPaymentModal = false"
            class="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="processPayment"
            :disabled="processing"
            class="flex-1 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-bold hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 flex items-center justify-center"
          >
            <i v-if="processing" class="fa-solid fa-spinner fa-spin mr-2"></i>
            {{ processing ? 'Processing...' : 'Pay $1.49 & Publish' }}
          </button>
        </div>

        <!-- Trust Badges -->
        <div class="mt-4 flex items-center justify-center space-x-4 text-xs text-gray-500">
          <span class="flex items-center">
            <i class="fa-solid fa-shield-alt text-green-600 mr-1"></i>
            Secure Payment
          </span>
          <span class="flex items-center">
            <i class="fa-solid fa-undo text-blue-600 mr-1"></i>
            Refund if Rejected
          </span>
          <span class="flex items-center">
            <i class="fa-solid fa-infinity text-purple-600 mr-1"></i>
            Forever Listing
          </span>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showSuccessModal = false"></div>
      <div class="relative bg-white rounded-lg max-w-md w-full p-6 md:p-8 shadow-xl text-center">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-xl md:text-2xl font-bold text-gray-900 mb-2">Product Published!</h3>
        <p class="text-gray-600 mb-6 text-sm md:text-base">Your product has been successfully listed on the marketplace.</p>
        <div class="flex flex-col sm:flex-row gap-3">
          <button 
            @click="goToShop"
            class="flex-1 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            View in Shop
          </button>
          <button 
            @click="createAnother"
            class="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            List Another
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
// Navbar is now in Layout component

const { t } = useI18n()

const router = useRouter()
const isSubmitting = ref(false)
const showPublishModal = ref(false)
const showPaymentModal = ref(false)
const processing = ref(false)
const paymentMethod = ref('usdt')

const form = reactive({
  name: '',
  category: '',
  price: '',
  originalPrice: '',
  deliveryType: '',
  updateFrequency: '',
  deliveryChannel: '',
  purposes: [],
  language: '',
  notificationEmail: '',
  notificationPhone: '',
  isOpenSource: false,
  supportNegotiation: false,
  supportCustomization: false,
  longTermSupport: false,
  acceptEscrow: false,
  images: [],
  video: null,
  shortDescription: '',
  description: '',
  featuresText: '',
  tagsText: '',
  version: '',
  license: 'lifetime'
})

// Import method selection
const importType = ref('manual') // 'repository' | 'cloud' | 'manual'

// Repository import
const repositoryUrl = ref('')
const importing = ref(false)
const importedData = ref(null)

// Cloud storage import
const cloudProvider = ref('baidu')
const storageType = ref('cloud-provider') // 'cloud-provider' | 'torrent' | 'self-hosted' | 'blockchain'
const storageLink = ref('')
const accessCode = ref('')
const torrentType = ref('magnet')
const magnetLink = ref('')
const torrentFile = ref(null)
const ipfsHash = ref('')
const downloadUrl = ref('')
const backupUrl = ref('')
const blockchainNetwork = ref('ipfs')
const blockchainHash = ref('')
const gatewayUrl = ref('')
const verifying = ref(false)
const verificationStatus = ref(null)
const verificationResult = ref(null)
const canSubmit = ref(true)

// Image Upload with Base64
const handleImageUpload = (event) => {
  const files = Array.from(event.target.files)
  const remainingSlots = 5 - form.images.length
  
  files.slice(0, remainingSlots).forEach(file => {
    if (file.size > 5 * 1024 * 1024) {
      alert(`File ${file.name} is too large. Max size is 5MB.`)
      return
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      form.images.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
  
  // Reset input
  event.target.value = ''
}

const removeImage = (index) => {
  form.images.splice(index, 1)
}

// Video Upload with Base64
const handleVideoUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (file.size > 50 * 1024 * 1024) {
    alert('Video file is too large. Max size is 50MB.')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    form.video = e.target.result
  }
  reader.readAsDataURL(file)
  
  // Reset input
  event.target.value = ''
}

const removeVideo = () => {
  form.video = null
}

// Form Submission
const handleSubmit = async () => {
  if (form.images.length === 0) {
    alert('Please upload at least one product image.')
    return
  }
  
  isSubmitting.value = true
  
  // Simulate API call
  setTimeout(() => {
    isSubmitting.value = false
    showSuccessModal.value = true
  }, 2000)
}

const handleSaveDraft = () => {
  alert('Draft saved successfully!')
}

const goToShop = () => {
  router.push('/shop')
}

const createAnother = () => {
  showSuccessModal.value = false
  // Reset form
  Object.keys(form).forEach(key => {
    if (Array.isArray(form[key])) {
      form[key] = []
    } else if (form[key] !== null && typeof form[key] === 'object') {
      form[key] = null
    } else {
      form[key] = key === 'license' ? 'lifetime' : ''
    }
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ============================================
// Repository Import Functions
// ============================================
const importFromRepo = async () => {
  if (!repositoryUrl.value) return
  
  importing.value = true
  try {
    // TODO: 调用后端AI API进行智能分析
    // const response = await aiApi.analyzeRepository(repositoryUrl.value)
    
    // Mock repository parsing (临时模拟)
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Simulate extracting data from repository
    const repoName = repositoryUrl.value.split('/').pop().replace('.git', '')
    importedData.value = {
      name: repoName.charAt(0).toUpperCase() + repoName.slice(1),
      description: `A powerful ${repoName} tool for developers`,
      version: '1.0.0',
      source: 'repository',
      url: repositoryUrl.value
    }
    
    // Auto-fill form with AI suggestions
    form.name = importedData.value.name
    form.description = importedData.value.description
    form.version = importedData.value.version
    form.category = 'software'
    form.shortDescription = `Powerful ${repoName} - Easy to use and efficient`
    form.tagsText = `${repoName}, developer tools, automation`
    form.featuresText = `- Easy installation\n- High performance\n- Well documented\n- Active community support`
    
    alert('�?Repository imported successfully!\n\nAI has analyzed your repository and auto-filled the form. Please review and adjust as needed.')
  } catch (error) {
    console.error('Import failed:', error)
    alert('�?Import failed: ' + error.message)
  } finally {
    importing.value = false
  }
}

const clearImportedData = () => {
  importedData.value = null
  repositoryUrl.value = ''
  storageLink.value = ''
  accessCode.value = ''
  magnetLink.value = ''
  torrentFile.value = null
  ipfsHash.value = ''
  downloadUrl.value = ''
  backupUrl.value = ''
  blockchainHash.value = ''
  gatewayUrl.value = ''
  verificationStatus.value = null
}

// ============================================
// Smart Progress Guide
// ============================================
const getProgressHint = () => {
  const filledFields = []
  if (form.name) filledFields.push('名称')
  if (form.category) filledFields.push('分类')
  if (form.price) filledFields.push('价格')
  if (form.description) filledFields.push('描述')
  if (form.images.length > 0) filledFields.push('图片')
  
  const totalFields = 5
  const progress = Math.round((filledFields.length / totalFields) * 100)
  
  if (progress === 0) return '开始填写吧�?
  if (progress < 40) return `已填�?${filledFields.join('�?)}，继续加油！`
  if (progress < 80) return `完成 ${progress}%！接下来填写${getNextSuggestion()}`
  return `太棒了！已完�?${progress}%，可以发布了 🎉`
}

const getNextSuggestion = () => {
  if (!form.price) return '价格 💰'
  if (!form.description) return '产品描述 📝'
  if (form.images.length === 0) return '产品图片 🖼�?
  if (!form.shortDescription) return '简短描�?�?
  if (!form.featuresText) return '功能特�?⚙️'
  return '最后检查即可发�?�?
}

// ============================================
// Cloud Storage Import Functions
// ============================================
const getStorageLinkPlaceholder = () => {
  const placeholders = {
    baidu: 'https://pan.baidu.com/s/1xxxxx',
    aliyun: 'https://www.aliyundrive.com/s/xxxxx',
    quark: 'https://pan.quark.cn/s/xxxxx',
    google: 'https://drive.google.com/file/d/xxxxx',
    dropbox: 'https://www.dropbox.com/s/xxxxx',
    onedrive: 'https://onedrive.live.com/?id=xxxxx',
    mega: 'https://mega.nz/file/xxxxx',
    other: 'https://...'
  }
  return placeholders[cloudProvider.value] || 'Paste share link here'
}

const getBlockchainHashPlaceholder = () => {
  const placeholders = {
    ipfs: 'QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco',
    arweave: 'W2_5ZqF8h9K3j4L6m7N8p9Q0r1S2t3U4v5W6x7Y8z9A0',
    filecoin: 'bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi',
    storj: 'ltus+2d3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z'
  }
  return placeholders[blockchainNetwork.value] || 'Enter content hash'
}

const getGatewayUrlPlaceholder = () => {
  const placeholders = {
    ipfs: 'https://ipfs.io/ipfs/QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco',
    arweave: 'https://arweave.net/W2_5ZqF8h9K3j4L6m7N8p9Q0r1S2t3U4v5W6x7Y8z9A0',
    filecoin: 'https://gateway.pinata.cloud/ipfs/bafybei...',
    storj: 'https://link.storjshare.io/s/ltus+2d3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z'
  }
  return placeholders[blockchainNetwork.value] || 'https://gateway.example.com/hash'
}

const handleTorrentUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  if (file.size > 1 * 1024 * 1024) {
    alert('.torrent file is too large. Max size is 1MB.')
    return
  }
  
  torrentFile.value = file
}

const verifyStorageLink = async () => {
  verifying.value = true
  verificationStatus.value = null
  
  try {
    // Mock verification - in production, this would call backend API
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    let result
    
    if (storageType.value === 'cloud-provider') {
      result = mockCloudLinkVerification(storageLink.value, cloudProvider.value)
    } else if (storageType.value === 'torrent') {
      if (torrentType.value === 'magnet') {
        result = mockMagnetLinkVerification(magnetLink.value)
      } else if (torrentType.value === 'ipfs') {
        result = mockIPFSVerification(ipfsHash.value)
      } else {
        result = mockTorrentFileVerification(torrentFile.value)
      }
    } else if (storageType.value === 'self-hosted') {
      result = mockSelfHostedVerification(downloadUrl.value)
    } else if (storageType.value === 'blockchain') {
      result = mockBlockchainVerification(blockchainHash.value, blockchainNetwork.value)
    }
    
    verificationStatus.value = result
    
    if (result.status === 'valid') {
      // Auto-fill form with detected info
      if (result.fileInfo) {
        form.name = form.name || result.fileInfo.name.replace(/\.[^/.]+$/, '')
        form.shortDescription = form.shortDescription || `High-quality ${result.fileInfo.type} resource`
      }
      alert('�?Verification passed! Link is accessible and valid.')
    } else {
      alert('�?Verification failed. Please check the link and try again.')
    }
  } catch (error) {
    verificationStatus.value = {
      status: 'invalid',
      message: 'Verification error occurred',
      details: error.message
    }
    alert('Verification failed: ' + error.message)
  } finally {
    verifying.value = false
  }
}

// Mock verification functions (replace with real API calls)
const mockCloudLinkVerification = (link, provider) => {
  // Simulate checking if link is accessible
  const isValid = link.includes('http') && link.length > 20
  
  if (!isValid) {
    return {
      status: 'invalid',
      message: 'Invalid link format',
      details: 'Please provide a valid share link from ' + provider
    }
  }
  
  // Mock file info extraction
  const mockFiles = [
    { name: 'Python Programming Guide.pdf', size: '25.5 MB', type: 'PDF Document', modified: '2024-01-15' },
    { name: 'Web Development Course.mp4', size: '1.2 GB', type: 'Video Course', modified: '2024-02-20' },
    { name: 'UI Design Templates.zip', size: '156 MB', type: 'ZIP Archive', modified: '2024-03-10' }
  ]
  const randomFile = mockFiles[Math.floor(Math.random() * mockFiles.length)]
  
  return {
    status: 'valid',
    message: 'Link is accessible and file is available',
    details: 'Successfully connected to ' + provider + '. File can be downloaded.',
    fileInfo: randomFile,
    accessibility: 'public',
    estimatedDownloadTime: '2-5 minutes'
  }
}

const mockMagnetLinkVerification = (magnet) => {
  const isValid = magnet.startsWith('magnet:?xt=urn:btih:')
  
  if (!isValid) {
    return {
      status: 'invalid',
      message: 'Invalid magnet link format',
      details: 'Magnet link should start with "magnet:?xt=urn:btih:"'
    }
  }
  
  return {
    status: 'valid',
    message: 'Magnet link format is valid',
    details: 'Note: Actual seed availability will be checked during manual review',
    fileInfo: {
      name: 'Detected Torrent Content',
      size: 'Unknown (requires DHT lookup)',
      type: 'Torrent',
      modified: 'N/A'
    },
    warning: 'You must maintain seeding for at least 30 days after sale'
  }
}

const mockIPFSVerification = (hash) => {
  const isValid = hash.length > 40 && (hash.startsWith('Qm') || hash.startsWith('bafy'))
  
  if (!isValid) {
    return {
      status: 'invalid',
      message: 'Invalid IPFS hash format',
      details: 'IPFS CID should be a valid base58 or base32 encoded string'
    }
  }
  
  return {
    status: 'valid',
    message: 'IPFS hash format is valid',
    details: 'Content can be retrieved via IPFS network',
    fileInfo: {
      name: 'IPFS Stored Content',
      size: 'Retrieved from IPFS network',
      type: 'Decentralized Storage',
      modified: 'Permanent'
    },
    advantage: 'Content is permanently stored and tamper-proof'
  }
}

const mockTorrentFileVerification = (file) => {
  if (!file) {
    return {
      status: 'invalid',
      message: 'No .torrent file uploaded',
      details: 'Please upload a valid .torrent file'
    }
  }
  
  return {
    status: 'valid',
    message: '.torrent file uploaded successfully',
    details: 'Torrent metadata will be analyzed during review',
    fileInfo: {
      name: file.name,
      size: (file.size / 1024).toFixed(2) + ' KB',
      type: 'Torrent File',
      modified: new Date().toISOString().split('T')[0]
    }
  }
}

const mockSelfHostedVerification = (url) => {
  const isValid = url.startsWith('https://') && url.length > 20
  
  if (!isValid) {
    return {
      status: 'invalid',
      message: 'Invalid URL format',
      details: 'Please provide a valid HTTPS URL'
    }
  }
  
  return {
    status: 'valid',
    message: 'URL format is valid',
    details: 'Server accessibility will be tested during review process',
    fileInfo: {
      name: 'Self-hosted Resource',
      size: 'Unknown (server response required)',
      type: 'Direct Download',
      modified: 'Check server headers'
    },
    recommendation: 'Consider adding a backup URL for redundancy'
  }
}

const mockBlockchainVerification = (hash, network) => {
  const isValid = hash.length > 30
  
  if (!isValid) {
    return {
      status: 'invalid',
      message: 'Invalid hash format for ' + network,
      details: 'Please provide a valid content identifier'
    }
  }
  
  return {
    status: 'valid',
    message: network + ' hash format is valid',
    details: 'Content is stored on decentralized network',
    fileInfo: {
      name: 'Blockchain Stored Content',
      size: 'Stored on ' + network,
      type: 'Decentralized Storage',
      modified: 'Immutable'
    },
    advantage: 'Permanent storage with cryptographic proof of integrity'
  }
}

// ============================================
// AI Content Verification Functions
// ============================================
const canVerify = computed(() => {
  return form.name && form.category && form.price && form.shortDescription
})

const runAIVerification = async () => {
  if (!canVerify.value) {
    alert('Please fill in basic product information first')
    return
  }
  
  verifying.value = true
  verificationResult.value = null
  
  try {
    // Build standardized product data for AI API
    const productData = buildStandardizedData()
    
    // Mock AI verification (replace with actual AI API call)
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Simulate AI verification result
    const mockResult = simulateAIVerification(productData)
    verificationResult.value = mockResult
    
    if (mockResult.status === 'approved') {
      canSubmit.value = true
      alert('�?AI verification passed! Your product meets all requirements.')
    } else {
      canSubmit.value = false
      alert('�?AI verification failed. Please fix the issues before submitting.')
    }
  } catch (error) {
    alert('AI verification failed: ' + error.message)
  } finally {
    verifying.value = false
  }
}

const buildStandardizedData = () => {
  return {
    productId: generateId(),
    timestamp: Date.now(),
    
    // Basic Information
    basicInfo: {
      name: form.name,
      category: form.category,
      price: parseFloat(form.price) || 0,
      originalPrice: parseFloat(form.originalPrice) || null,
      currency: 'USDT',
      version: form.version || '1.0.0',
      license: form.license
    },
    
    // Media Assets
    media: {
      images: form.images.map((img, idx) => ({
        id: idx,
        url: img,
        type: 'image'
      })),
      video: form.video ? {
        url: form.video,
        type: 'video'
      } : null,
      files: platformFiles.value.map((file, idx) => ({
        id: idx,
        name: file.name,
        size: file.size,
        type: file.type
      }))
    },
    
    // Content Description
    content: {
      shortDescription: form.shortDescription,
      fullDescription: form.description,
      features: form.featuresText.split('\n').filter(f => f.trim()),
      tags: form.tagsText.split(',').map(t => t.trim()).filter(t => t)
    },
    
    // Source Information
    source: {
      type: importType.value,
      url: importType.value === 'repository' ? repositoryUrl.value :
           importType.value === 'cloud' ? storageLink.value : null,
      provider: importType.value === 'cloud' ? cloudProvider.value : null,
      
      // Storage location details (NEW)
      storageLocation: importType.value === 'cloud' ? {
        storageType: storageType.value,
        cloudProvider: cloudProvider.value,
        accessCode: accessCode.value || null,
        torrentType: torrentType.value || null,
        magnetLink: magnetLink.value || null,
        ipfsHash: ipfsHash.value || null,
        downloadUrl: downloadUrl.value || null,
        backupUrl: backupUrl.value || null,
        blockchainNetwork: blockchainNetwork.value || null,
        blockchainHash: blockchainHash.value || null,
        gatewayUrl: gatewayUrl.value || null
      } : null
    },
    
    // Additional Metadata
    metadata: {
      deliveryType: form.deliveryType || null,
      updateFrequency: form.updateFrequency || null,
      deliveryChannel: form.deliveryChannel || null,
      purposes: form.purposes || [],
      programmingLanguage: form.language || null,
      notificationContact: {
        email: form.notificationEmail || null,
        phone: form.notificationPhone || null
      },
      isOpenSource: form.isOpenSource || false,
      supportOptions: {
        negotiation: form.supportNegotiation || false,
        customization: form.supportCustomization || false,
        longTermSupport: form.longTermSupport || false,
        escrow: form.acceptEscrow || false
      }
    },
    
    // Verification Status
    verification: {
      status: 'pending', // 'pending' | 'approved' | 'rejected'
      timestamp: null,
      issues: [],
      confidence: null
    }
  }
}

const simulateAIVerification = (productData) => {
  // Mock AI verification logic
  const issues = []
  let status = 'approved'
  let confidence = 0.95
  
  // Check 1: Title quality
  if (productData.basicInfo.name.length < 5) {
    issues.push({
      type: 'warning',
      field: 'name',
      message: 'Product name is too short. Please provide a more descriptive name.',
      severity: 'medium'
    })
    confidence -= 0.1
  }
  
  // Check 2: Description completeness
  if (!productData.content.fullDescription || productData.content.fullDescription.length < 50) {
    issues.push({
      type: 'error',
      field: 'description',
      message: 'Product description is too brief. Please provide at least 50 characters.',
      severity: 'high'
    })
    status = 'rejected'
    confidence -= 0.3
  }
  
  // Check 3: Price合理�?
  if (productData.basicInfo.price <= 0) {
    issues.push({
      type: 'error',
      field: 'price',
      message: 'Price must be greater than 0.',
      severity: 'high'
    })
    status = 'rejected'
    confidence -= 0.3
  }
  
  // Check 4: Image requirement
  if (productData.media.images.length === 0 && !productData.source.url) {
    issues.push({
      type: 'warning',
      field: 'images',
      message: 'No product images uploaded. Consider adding images to improve trust.',
      severity: 'low'
    })
    confidence -= 0.05
  }
  
  // Check 5: Suspicious content detection (mock)
  const suspiciousKeywords = ['free', 'crack', 'pirated', 'illegal']
  const fullText = `${productData.basicInfo.name} ${productData.content.shortDescription} ${productData.content.fullDescription}`.toLowerCase()
  
  suspiciousKeywords.forEach(keyword => {
    if (fullText.includes(keyword)) {
      issues.push({
        type: 'error',
        field: 'content',
        message: `Detected potentially problematic keyword: "${keyword}". Please ensure content complies with platform policies.`,
        severity: 'critical'
      })
      status = 'rejected'
      confidence -= 0.4
    }
  })
  
  // Check 6: Category appropriateness
  const categoryKeywords = {
    ebooks: ['book', 'guide', 'handbook', 'pdf', 'epub'],
    courses: ['course', 'tutorial', 'training', 'lesson', 'video'],
    software: ['tool', 'app', 'application', 'software', 'program']
  }
  
  const category = productData.basicInfo.category
  if (categoryKeywords[category]) {
    const hasRelevantKeyword = categoryKeywords[category].some(keyword => 
      fullText.includes(keyword)
    )
    
    if (!hasRelevantKeyword) {
      issues.push({
        type: 'warning',
        field: 'category',
        message: `Selected category "${category}" may not match product content. Please verify.`,
        severity: 'medium'
      })
      confidence -= 0.1
    }
  }
  
  // Check 7: Storage location verification (NEW - Critical for authenticity)
  if (productData.source.type === 'cloud' && productData.source.storageLocation) {
    const storage = productData.source.storageLocation
    
    // Verify storage type is specified
    if (!storage.storageType) {
      issues.push({
        type: 'error',
        field: 'storageLocation',
        message: 'Storage location type is required. Please specify where your files are stored.',
        severity: 'high'
      })
      status = 'rejected'
      confidence -= 0.3
    }
    
    // Verify cloud provider links
    if (storage.storageType === 'cloud-provider') {
      if (!storage.cloudProvider) {
        issues.push({
          type: 'error',
          field: 'cloudProvider',
          message: 'Please select a cloud storage provider.',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.2
      }
      
      if (!storage.url || storage.url.length < 10) {
        issues.push({
          type: 'error',
          field: 'storageLink',
          message: 'Valid share link is required for cloud storage.',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.3
      }
      
      // Check if access code is provided for Chinese cloud drives
      const chineseProviders = ['baidu', 'aliyun', 'quark']
      if (chineseProviders.includes(storage.cloudProvider) && !storage.accessCode) {
        issues.push({
          type: 'warning',
          field: 'accessCode',
          message: `${storage.cloudProvider} typically requires an access code. Please provide it if needed.`,
          severity: 'medium'
        })
        confidence -= 0.05
      }
    }
    
    // Verify torrent/P2P storage
    if (storage.storageType === 'torrent') {
      if (storage.torrentType === 'magnet' && (!storage.magnetLink || !storage.magnetLink.startsWith('magnet:?'))) {
        issues.push({
          type: 'error',
          field: 'magnetLink',
          message: 'Invalid magnet link format. Must start with "magnet:?xt=urn:btih:"',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.3
      }
      
      if (storage.torrentType === 'ipfs' && (!storage.ipfsHash || storage.ipfsHash.length < 40)) {
        issues.push({
          type: 'error',
          field: 'ipfsHash',
          message: 'Invalid IPFS hash. Please provide a valid Content Identifier (CID).',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.3
      }
      
      // Add warning about seeding responsibility
      issues.push({
        type: 'info',
        field: 'torrent',
        message: 'Remember: You must maintain active seeding for at least 30 days after sale. Failure to seed may result in penalties.',
        severity: 'low'
      })
    }
    
    // Verify self-hosted server
    if (storage.storageType === 'self-hosted') {
      if (!storage.downloadUrl || !storage.downloadUrl.startsWith('https://')) {
        issues.push({
          type: 'error',
          field: 'downloadUrl',
          message: 'Self-hosted storage requires a valid HTTPS download URL.',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.3
      }
      
      if (!storage.backupUrl) {
        issues.push({
          type: 'warning',
          field: 'backupUrl',
          message: 'Backup URL is recommended for self-hosted storage to ensure reliability.',
          severity: 'medium'
        })
        confidence -= 0.1
      }
    }
    
    // Verify blockchain/IPFS storage
    if (storage.storageType === 'blockchain') {
      if (!storage.blockchainNetwork) {
        issues.push({
          type: 'error',
          field: 'blockchainNetwork',
          message: 'Please select a blockchain network (IPFS, Arweave, etc.).',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.2
      }
      
      if (!storage.blockchainHash || storage.blockchainHash.length < 30) {
        issues.push({
          type: 'error',
          field: 'blockchainHash',
          message: 'Valid content hash/CID is required for blockchain storage.',
          severity: 'high'
        })
        status = 'rejected'
        confidence -= 0.3
      } else {
        // Positive note for blockchain storage
        recommendations.push('�?Blockchain storage provides permanent, tamper-proof storage - excellent choice!')
      }
    }
  } else if (productData.source.type === 'cloud') {
    issues.push({
      type: 'error',
      field: 'storageLocation',
      message: 'Storage location information is missing. Please specify where your product files are stored.',
      severity: 'critical'
    })
    status = 'rejected'
    confidence -= 0.4
  }
  
  return {
    status,
    timestamp: new Date().toISOString(),
    issues,
    confidence: Math.max(0, confidence),
    recommendations: generateRecommendations(issues),
    aiModel: 'ContentVerifier-v2.1',
    processingTime: '2.8s'
  }
}

const generateRecommendations = (issues) => {
  const recommendations = []
  
  if (issues.some(i => i.field === 'description')) {
    recommendations.push('Add detailed product features and benefits to increase buyer confidence.')
  }
  
  if (issues.some(i => i.field === 'images')) {
    recommendations.push('Upload high-quality screenshots or demo images to showcase your product.')
  }
  
  if (issues.some(i => i.severity === 'critical')) {
    recommendations.push('Review platform policies and ensure all content complies with guidelines.')
  }
  
  if (recommendations.length === 0) {
    recommendations.push('Your product looks great! Consider adding customer testimonials or reviews.')
  }
  
  return recommendations
}

// ============================================
// Publish & Payment Functions
// ============================================

const canPublish = computed(() => {
  // Must have basic info filled
  const hasBasicInfo = form.name && form.category && form.price && form.shortDescription
  
  // If audit not run yet, allow clicking to trigger audit
  if (!verificationResult.value) {
    return hasBasicInfo
  }
  
  // If audit passed or has only warnings, allow publish
  if (verificationResult.value.status === 'approved') {
    return true
  }
  
  // If rejected with critical errors, don't allow
  const hasCriticalErrors = verificationResult.value.issues.some(
    issue => issue.severity === 'critical' || issue.severity === 'high'
  )
  
  return !hasCriticalErrors
})

const auditPassed = computed(() => {
  if (!verificationResult.value) return false
  return verificationResult.value.status === 'approved'
})

const getCategoryLabel = (category) => {
  const labels = {
    'short-video': 'Short Video',
    'article': 'Article',
    'software': 'Software & Tools',
    'web-app': 'Website/App Source Code',
    'ebooks': 'E-books',
    'courses': 'Learning Courses',
    'design': 'Design Resources',
    'services': 'Comprehensive Services',
    'ai-tools': 'AI Tools'
  }
  return labels[category] || category
}

// Delivery type options based on category
const deliveryTypeOptions = computed(() => {
  const allOptions = [
    { value: 'source-code', label: 'Source Code Delivery', icon: 'fa-code' },
    { value: 'long-term', label: 'Long-term Delivery (Regular Updates)', icon: 'fa-sync-alt' },
    { value: 'tiered', label: 'Tiered Delivery (Basic/Premium/VIP)', icon: 'fa-layer-group' },
    { value: 'application', label: 'Application Delivery', icon: 'fa-desktop' },
    { value: 'document', label: 'Electronic Document Delivery', icon: 'fa-file-alt' },
    { value: 'image', label: 'Image Delivery', icon: 'fa-image' },
    { value: 'api', label: 'API Delivery', icon: 'fa-plug' },
    { value: 'other', label: 'Other Delivery Method', icon: 'fa-ellipsis-h' }
  ]

  // Category-based filtering rules
  const categoryRules = {
    'short-video': ['long-term', 'tiered', 'api'],
    'article': ['document', 'long-term', 'tiered'],
    'software': ['source-code', 'application', 'api', 'long-term'],
    'web-app': ['source-code', 'application', 'api', 'long-term'],
    'ebooks': ['document', 'tiered'],
    'courses': ['long-term', 'tiered', 'document', 'api'],
    'design': ['image', 'source-code', 'tiered'],
    'services': ['long-term', 'tiered', 'api', 'other'],
    'ai-tools': ['api', 'application', 'source-code', 'long-term']
  }

  const allowedTypes = categoryRules[form.category] || allOptions.map(opt => opt.value)
  return allOptions.filter(opt => allowedTypes.includes(opt.value))
})

const getDeliveryTypeLabel = (value) => {
  const option = deliveryTypeOptions.value.find(opt => opt.value === value)
  return option ? option.label : value
}

const handlePublishClick = () => {
  if (!verificationResult.value) {
    // First time - show publish flow modal
    showPublishModal.value = true
  } else if (auditPassed.value || canPublish.value) {
    // Audit passed - show payment modal
    showPaymentModal.value = true
  } else {
    // Audit failed - show error
    alert('请先修复问题后再发布。查看AI审计报告了解详情�?)
  }
}

// 确认发布
const confirmPublish = async () => {
  showPublishModal.value = false
  
  // 显示加载状�?
  verifying.value = true
  
  try {
    // TODO: 调用后端API发布商品到AI市场
    // await productsApi.publishToAIMarket(buildStandardizedData())
    
    // 模拟发布成功
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 发布成功提示
    alert('�?发布成功！\n\n您的商品已提交到AI市场，将进入审核流程。\n请查看邮件或手机通知获取审计报告�?)
    
    // 重置表单
    // TODO: 跳转到订单状态页或我的商品页
    // router.push('/my-products')
    
  } catch (error) {
    console.error('发布失败:', error)
    alert('�?发布失败\n\n' + (error.message || '请稍后重�?))
  } finally {
    verifying.value = false
  }
}

const processPayment = async () => {
  processing.value = true
  
  try {
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock successful payment
    console.log('Payment processed:', {
      amount: 1.49,
      currency: 'USDT',
      method: paymentMethod.value,
      productId: generateId()
    })
    
    // Close payment modal
    showPaymentModal.value = false
    
    // Show success modal
    showSuccessModal.value = true
    
    // In production, this would:
    // 1. Call backend API to create product
    // 2. Process blockchain transaction
    // 3. Wait for confirmation
    // 4. Publish to marketplace
    
  } catch (error) {
    alert('Payment failed: ' + error.message)
  } finally {
    processing.value = false
  }
}

const generateId = () => {
  return 'prod_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}
</script>
