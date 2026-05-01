<template>
  <div class="w-full bg-gradient-to-br from-gray-50 via-blue-50/30 to-blue-50/20">
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="max-w-7xl mx-auto">
        
        <!-- View Mode Toggle Switch -->
        <div class="mb-6 flex items-center justify-end">
          <div class="flex items-center space-x-3 bg-white px-4 py-2.5 rounded-lg shadow-sm border border-gray-200">
            <span class="text-sm font-medium text-gray-700">Hiển thị theo Module</span>
            <label class="relative inline-flex items-center cursor-pointer">
              <input 
                type="checkbox" 
                v-model="showByProduct"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
            <span class="text-sm font-medium text-gray-700">Hiển thị theo Sản phẩm</span>
          </div>
        </div>
        
        <!-- Product Navigation (Level 1) - Card Style -->
        <div v-if="showByProduct" class="mb-8">
          <h2 class="text-lg font-semibold text-gray-700 mb-4">Chọn Sản phẩm</h2>
          <div class="flex overflow-x-auto scrollbar-hide gap-8 pb-3" style="scrollbar-width: thin;">
            <button
              v-for="product in products"
              :key="product.id"
              @click="selectedProduct = product.id"
              class="group relative bg-white p-0 shadow-2xl border-2 transition-all duration-300 hover:shadow-3xl hover:-translate-y-1 flex-shrink-0 product-card-3d overflow-hidden"
              :class="[
                selectedProduct === product.id
                  ? 'border-blue-600 product-card-selected'
                  : 'border-gray-300 hover:border-blue-400'
              ]"
              style="width: 140px; height: 140px;">
              <!-- Selected Indicator -->
              <div v-if="selectedProduct === product.id" 
                   class="absolute top-2 right-2 w-4.5 h-4.5 bg-blue-600 rounded-full flex items-center justify-center shadow-xl z-10 border-2 border-white">
                <svg class="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
              </div>

              <!-- Product Logo - Full Frame -->
              <div class="w-full h-full flex items-center justify-center product-logo-full-frame">
                <img 
                  v-if="product.logo"
                  :src="product.logo" 
                  :alt="product.name"
                  class="w-full h-full object-cover transition-all duration-300 group-hover:scale-110"
                  @error="handleImageError"
                />
                <div 
                  v-else
                  class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center transition-all duration-300 group-hover:scale-110"
                  :class="selectedProduct === product.id ? 'from-blue-100 to-blue-200' : ''">
                  <component 
                    :is="product.icon || Brain" 
                    :size="56" 
                    class="transition-all duration-300"
                    :class="selectedProduct === product.id ? 'text-blue-600' : 'text-gray-500'" />
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- Module Navigation (Level 2) - Grid Layout -->
        <div v-if="displayModules.length > 0" class="mb-8">
          <h2 class="text-base font-semibold text-gray-700 mb-4">
            <span v-if="showByProduct">Modules của <span class="text-blue-600">{{ currentProduct.name }}</span></span>
            <span v-else>Chọn Module</span>
          </h2>
          
          <!-- Module Grid Container -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            <button
              v-for="module in displayModulesWithCount"
              :key="module.id"
              @click="selectedModule = module.id"
              class="group relative bg-white rounded-lg p-3 shadow-sm transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 flex flex-col items-center justify-center space-y-2"
              :class="[
                selectedModule === module.id
                  ? 'bg-blue-50/80'
                  : 'hover:bg-blue-50/30'
              ]">
              
              <!-- Module Icon - Circular -->
              <div 
                class="w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300"
                :class="module.bgColor">
                <component 
                  :is="module.icon" 
                  :size="22"
                  class="text-white" />
              </div>
              
              <!-- Agent Count - Large Number -->
              <div 
                class="text-2xl font-bold"
                :class="module.bgColor.replace('bg-', 'text-')">
                {{ module.count }}
              </div>
              
              <!-- Module Name -->
              <div class="text-center">
                <span 
                  class="text-xs font-medium leading-tight text-gray-700">
                  {{ module.name }}
                </span>
              </div>
            </button>
          </div>
        </div>

        <!-- AI Agents Filter Bar -->
        <div v-if="filteredAgents.length > 0" class="mb-4">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-2.5">
            <div class="flex flex-col md:flex-row gap-2">
              <!-- Search Input -->
              <div class="flex-1 relative">
                <svg class="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" 
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Tìm kiếm AI Agent..."
                  class="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <!-- Status Filter -->
              <select
                v-model="statusFilter"
                class="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="">Tất cả trạng thái</option>
                <option value="active">Đang hoạt động</option>
                <option value="deployed">Đã triển khai</option>
                <option value="inactive">Không hoạt động</option>
              </select>

              <!-- Source Filter -->
              <select
                v-model="sourceFilter"
                class="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="">Tất cả nguồn</option>
                <option value="Control Tower">Control Tower</option>
                <option value="System">System</option>
              </select>

              <!-- Clear Filters Button -->
              <button
                v-if="hasActiveFilters"
                @click="clearFilters"
                class="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors flex items-center space-x-1.5"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
                <span>Xóa bộ lọc</span>
              </button>
            </div>

            <!-- Active Filters Count -->
            <div v-if="hasActiveFilters" class="mt-2 flex items-center space-x-1.5 text-xs text-gray-600">
              <span class="font-semibold">{{ finalFilteredAgents.length }}</span>
              <span>kết quả được tìm thấy</span>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="text-center py-20">
          <div class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-blue-600 border-t-transparent"></div>
          <p class="mt-6 text-gray-600 text-lg">Đang tải dữ liệu...</p>
        </div>

        <!-- AI Agents Grid -->
        <div v-else-if="finalFilteredAgents.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="agent in finalFilteredAgents"
            :key="agent.docName"
            class="group bg-white rounded-2xl p-6 shadow-lg border border-gray-200 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer"
            @click="viewAgentDetails(agent)">
            
            <!-- Agent Header -->
            <div class="mb-4">
              <div class="flex items-start justify-between mb-3">
                <div 
                  class="w-14 h-14 rounded-xl flex items-center justify-center shadow-md transition-transform duration-300 group-hover:scale-110"
                  :class="agent.iconBg || 'bg-blue-500'">
                  <component :is="agent.icon || Brain" :size="28" class="text-white" />
                </div>
                <div class="flex flex-col items-end space-y-1.5">
                  <span 
                    v-if="agent.isNew"
                    class="px-2 py-0.5 rounded-full text-xs font-bold bg-orange-500 text-white flex items-center space-x-1 shadow-sm">
                    <span>NEW</span>
                  </span>
                  <span 
                    v-if="agent.status === 'deployed'"
                    class="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700 flex items-center space-x-1">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <span>Đã triển khai</span>
                  </span>
                </div>
              </div>
              
              <h3 class="text-xl font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                {{ agent.name }}
              </h3>
              <p class="text-sm text-gray-500 font-medium">{{ agent.nameEn }}</p>
            </div>

            <!-- Description -->
            <p class="text-gray-600 text-sm mb-4 line-clamp-2">
              {{ agent.description }}
            </p>

            <!-- Capabilities -->
            <div class="mb-4">
              <h4 class="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-1">
                <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                  <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd"/>
                </svg>
                <span>Khả năng</span>
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(capability, index) in agent.capabilities.slice(0, 3)"
                  :key="index"
                  class="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-medium">
                  {{ capability }}
                </span>
                <span 
                  v-if="agent.capabilities.length > 3"
                  class="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-lg text-xs font-medium">
                  +{{ agent.capabilities.length - 3 }} khác
                </span>
              </div>
            </div>

            <!-- Footer -->
            <div class="pt-4 border-t border-gray-100 flex items-center justify-end">
              <button class="text-blue-600 hover:text-blue-700 font-semibold text-sm flex items-center space-x-1 group-hover:space-x-2 transition-all">
                <span>Chi tiết</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State - No Agents -->
        <div v-else-if="selectedModule && filteredAgents.length === 0" class="text-center py-20">
          <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <component :is="currentModule?.icon || Brain" :size="48" class="text-gray-400" />
          </div>
          <h3 class="text-2xl font-semibold text-gray-900 mb-2">Chưa có AI Agents</h3>
          <p class="text-gray-600 text-lg">Module này chưa có AI Agent nào được cấu hình.</p>
        </div>

        <!-- Empty State - No Results from Filter -->
        <div v-else-if="filteredAgents.length > 0 && finalFilteredAgents.length === 0" class="text-center py-20">
          <div class="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
            <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
          <h3 class="text-2xl font-semibold text-gray-900 mb-2">Không tìm thấy kết quả</h3>
          <p class="text-gray-600 text-lg mb-4">Không có AI Agent nào phù hợp với bộ lọc của bạn.</p>
          <button
            @click="clearFilters"
            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold">
            Xóa bộ lọc
          </button>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import dbizErpLogo from '@/assets/dbiz_erp.png'
import dbizCxLogo from '@/assets/dbiz_cx.png'
import dbizDataLogo from '@/assets/dbiz_data.png'
import dbizMicrosmeLogo from '@/assets/dbiz_microsme.png'
import { 
  DollarSign, 
  Truck, 
  Factory, 
  Users, 
  Brain,
  FileText,
  Receipt,
  TrendingUp,
  CheckCircle,
  Calendar,
  Package,
  ShoppingCart,
  Briefcase,
  UserCheck,
  Calculator,
  ClipboardCheck,
  Layers,
  MessageSquare,
  Database,
  Building,
  Link,
  Grid3x3,
  Settings,
  TrendingDown,
  Activity
} from 'lucide-vue-next'

// Icon mapping
const iconMap = {
  'DollarSign': DollarSign,
  'Truck': Truck,
  'Factory': Factory,
  'Users': Users,
  'Brain': Brain,
  'FileText': FileText,
  'Receipt': Receipt,
  'TrendingUp': TrendingUp,
  'CheckCircle': CheckCircle,
  'Calendar': Calendar,
  'Package': Package,
  'ShoppingCart': ShoppingCart,
  'Briefcase': Briefcase,
  'UserCheck': UserCheck,
  'Calculator': Calculator,
  'ClipboardCheck': ClipboardCheck,
  'Layers': Layers,
  'MessageSquare': MessageSquare,
  'Database': Database,
  'Building': Building,
  'Link': Link,
  'Grid3x3': Grid3x3,
  'Settings': Settings,
  'TrendingDown': TrendingDown,
  'Activity': Activity
}

// State
const isLoading = ref(false)
const products = ref([
  {
    id: 'dbiz-erp',
    name: 'DBIZ ERP',
    icon: Layers,
    logo: dbizErpLogo,
    modules: ['finance', 'supply-chain', 'manufacturing', 'hr'],
    totalAgents: 18
  },
  {
    id: 'dbiz-cx',
    name: 'DBIZ CX',
    icon: MessageSquare,
    logo: dbizCxLogo,
    modules: ['general'],
    totalAgents: 8
  },
  {
    id: 'dbiz-data',
    name: 'DBIZ DATA',
    icon: Database,
    logo: dbizDataLogo,
    modules: ['general'],
    totalAgents: 4
  },
  {
    id: 'dbiz-microsme',
    name: 'DBIZ microSME',
    icon: Building,
    logo: dbizMicrosmeLogo,
    modules: ['finance', 'supply-chain', 'hr'],
    totalAgents: 12
  }
])

// Module definitions
const modules = ref([
  {
    id: 'finance',
    name: 'Tài chính & Kế toán',
    description: 'AI Agents tự động hóa quy trình tài chính, dự báo dòng tiền và phát hiện bất thường',
    icon: DollarSign,
    bgColor: 'bg-teal-600',
    count: 12
  },
  {
    id: 'supply-chain',
    name: 'Chuỗi cung ứng & Logistics',
    description: 'Tối ưu hóa vận chuyển, quản lý kho và dự báo nhu cầu',
    icon: Truck,
    bgColor: 'bg-amber-500',
    count: 11
  },
  {
    id: 'manufacturing',
    name: 'Sản xuất (MES/APS)',
    description: 'Lập lịch sản xuất thông minh và giám sát chất lượng',
    icon: Factory,
    bgColor: 'bg-pink-600',
    count: 6
  },
  {
    id: 'hr',
    name: 'Nhân sự & Lương',
    description: 'Tự động hóa quy trình nhân sự và tính lương',
    icon: Users,
    bgColor: 'bg-orange-600',
    count: 7
  },
  {
    id: 'sales-marketing',
    name: 'Bán hàng & Marketing',
    description: 'AI Agents hỗ trợ bán hàng và marketing tự động',
    icon: ShoppingCart,
    bgColor: 'bg-purple-600',
    count: 13
  },
  {
    id: 'customer-experience',
    name: 'Trải nghiệm Khách hàng (CX)',
    description: 'AI Agents tự động hóa chăm sóc khách hàng và cải thiện trải nghiệm',
    icon: MessageSquare,
    bgColor: 'bg-orange-600',
    count: 11
  },
  {
    id: 'data-management',
    name: 'Quản trị Dữ liệu & Analytics',
    description: 'AI Agents phân tích dữ liệu, tạo insights và dự báo xu hướng',
    icon: Database,
    bgColor: 'bg-blue-600',
    count: 27
  },
  {
    id: 'integration-automation',
    name: 'Tích hợp & Tự động hóa',
    description: 'AI Agents tự động hóa tích hợp hệ thống và quy trình',
    icon: Link,
    bgColor: 'bg-gray-500',
    count: 9
  },
  {
    id: 'general',
    name: 'Chung & Khác',
    description: 'Các AI Agents đa năng và tiện ích chung',
    icon: Brain,
    bgColor: 'bg-lime-500',
    count: 12
  }
])

// AI Agents data
const agents = ref([
  // Finance & Accounting
  {
    id: 1,
    module: 'finance',
    name: 'Trợ lý Xử lý Hóa đơn AI',
    nameEn: 'Invoice Processing Agent',
    description: 'Tự động trích xuất và xử lý hóa đơn từ scan/email với OCR thông minh, đối soát 3 bên tự động, phát hiện hóa đơn trùng lặp',
    icon: Receipt,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Trích xuất dữ liệu từ hóa đơn bằng OCR',
      'Đối soát 3 bên tự động',
      'Phát hiện hóa đơn trùng lặp',
      'Tự động nhập vào hệ thống kế toán',
      'Xác thực thông tin nhà cung cấp'
    ],
    source: 'Control Tower',
    status: 'active'
  },
  {
    id: 2,
    module: 'finance',
    name: 'Trợ lý Phê duyệt Chi phí AI',
    nameEn: 'Expense Approval Agent',
    description: 'Phê duyệt chi phí tự động theo policy, OCR receipt và xác thực, workflow approval tự động đa cấp',
    icon: CheckCircle,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Phê duyệt chi phí theo policy',
      'OCR receipt tự động',
      'Workflow approval đa cấp',
      'Phát hiện chi phí bất thường',
      'Tích hợp với hệ thống kế toán'
    ],
    source: 'Control Tower',
    status: 'active'
  },
  {
    id: 3,
    module: 'finance',
    name: 'Trợ lý Dự báo Tài chính AI',
    nameEn: 'Cash Flow Forecast Agent',
    description: 'Dự báo dòng tiền và báo cáo tài chính tự động, phân tích báo cáo tài chính, scenario planning',
    icon: TrendingUp,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Dự báo dòng tiền 30-90 ngày',
      'Phân tích lịch sử dòng tiền',
      'Scenario planning',
      'Cảnh báo thiếu hụt tiền mặt',
      'Báo cáo tài chính tự động'
    ],
    source: 'System',
    status: 'deployed'
  },
  {
    id: 4,
    module: 'finance',
    name: 'Trợ lý Đối chiếu Công nợ',
    nameEn: 'Account Reconciliation Agent',
    description: 'Đối chiếu công nợ tự động, phát hiện sai lệch và gửi thông báo',
    icon: Calculator,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Đối chiếu công nợ khách hàng',
      'Đối chiếu công nợ nhà cung cấp',
      'Phát hiện sai lệch tự động',
      'Gửi thông báo nhắc nợ',
      'Báo cáo công nợ định kỳ'
    ],
    source: 'Control Tower',
    status: 'active'
  },
  {
    id: 5,
    module: 'finance',
    name: 'Trợ lý Kiểm toán AI',
    nameEn: 'Audit Assistant Agent',
    description: 'Hỗ trợ kiểm toán tự động, phát hiện gian lận và bất thường trong dữ liệu tài chính',
    icon: ClipboardCheck,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Phân tích dữ liệu giao dịch',
      'Phát hiện gian lận',
      'Kiểm tra tuân thủ chính sách',
      'Báo cáo rủi ro tự động',
      'Đề xuất cải thiện quy trình'
    ],
    source: 'Control Tower',
    status: 'active'
  },

  // Supply Chain & Logistics
  {
    id: 6,
    module: 'supply-chain',
    name: 'Trợ lý Tối ưu Vận chuyển',
    nameEn: 'Route Optimization Agent',
    description: 'Tối ưu hóa tuyến đường vận chuyển, tiết kiệm chi phí và thời gian giao hàng',
    icon: Truck,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Tối ưu tuyến đường giao hàng',
      'Tính toán chi phí vận chuyển',
      'Theo dõi đơn hàng real-time',
      'Dự báo thời gian giao hàng',
      'Phân bổ xe và tài xế'
    ],
    source: 'Control Tower',
    status: 'active'
  },
  {
    id: 7,
    module: 'supply-chain',
    name: 'Trợ lý Quản lý Kho',
    nameEn: 'Warehouse Management Agent',
    description: 'Quản lý tồn kho thông minh, dự báo nhu cầu và tự động đặt hàng',
    icon: Package,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Theo dõi tồn kho real-time',
      'Dự báo nhu cầu hàng hóa',
      'Tự động đặt hàng bù',
      'Cảnh báo hàng sắp hết',
      'Tối ưu vị trí lưu kho'
    ],
    source: 'Control Tower',
    status: 'deployed'
  },
  {
    id: 8,
    module: 'supply-chain',
    name: 'Trợ lý Đàm phán Nhà cung cấp',
    nameEn: 'Supplier Negotiation Agent',
    description: 'Hỗ trợ đàm phán giá và điều khoản với nhà cung cấp dựa trên dữ liệu thị trường',
    icon: Briefcase,
    iconBg: 'bg-blue-500',
    capabilities: [
      'Phân tích giá thị trường',
      'Đề xuất mức giá hợp lý',
      'So sánh nhà cung cấp',
      'Theo dõi hợp đồng',
      'Đánh giá hiệu suất nhà cung cấp'
    ],
    source: 'Control Tower',
    status: 'active'
  },

  // Manufacturing (MES/APS)
  {
    id: 9,
    module: 'manufacturing',
    name: 'Trợ lý Lập lịch Sản xuất',
    nameEn: 'Production Planning Agent',
    description: 'Lập lịch sản xuất tự động, tối ưu hóa công suất và giảm thời gian chết',
    icon: Calendar,
    iconBg: 'bg-green-500',
    capabilities: [
      'Lập lịch sản xuất tự động',
      'Tối ưu công suất máy móc',
      'Phân bổ nguyên vật liệu',
      'Dự báo thời gian hoàn thành',
      'Xử lý đơn hàng khẩn cấp'
    ],
    source: 'Control Tower',
    status: 'deployed'
  },
  {
    id: 10,
    module: 'manufacturing',
    name: 'Trợ lý Kiểm soát Chất lượng',
    nameEn: 'Quality Control Agent',
    description: 'Giám sát chất lượng sản phẩm, phát hiện lỗi và đề xuất cải tiến',
    icon: ClipboardCheck,
    iconBg: 'bg-green-500',
    capabilities: [
      'Kiểm tra chất lượng tự động',
      'Phát hiện sản phẩm lỗi',
      'Phân tích nguyên nhân lỗi',
      'Báo cáo chất lượng',
      'Đề xuất cải tiến quy trình'
    ],
    source: 'Control Tower',
    status: 'active'
  },

  // HR & Payroll
  {
    id: 11,
    module: 'hr',
    name: 'Trợ lý Tuyển dụng AI',
    nameEn: 'Recruitment Assistant Agent',
    description: 'Sàng lọc CV tự động, đề xuất ứng viên phù hợp và lập lịch phỏng vấn',
    icon: UserCheck,
    iconBg: 'bg-orange-500',
    capabilities: [
      'Sàng lọc CV tự động',
      'Đề xuất ứng viên phù hợp',
      'Lập lịch phỏng vấn',
      'Đánh giá kỹ năng',
      'Gửi thông báo tự động'
    ],
    source: 'Control Tower',
    status: 'active'
  },
  {
    id: 12,
    module: 'hr',
    name: 'Trợ lý Tính lương AI',
    nameEn: 'Payroll Processing Agent',
    description: 'Tính lương tự động, kiểm tra tuân thủ và tạo báo cáo lương',
    icon: Calculator,
    iconBg: 'bg-orange-500',
    capabilities: [
      'Tính lương tự động',
      'Tính thuế thu nhập cá nhân',
      'Tính bảo hiểm xã hội',
      'Tạo phiếu lương',
      'Báo cáo chi phí nhân sự'
    ],
    source: 'Control Tower',
    status: 'deployed'
  },

  // General & Others
  {
    id: 13,
    module: 'general',
    name: 'Trợ lý Chatbot Đa năng',
    nameEn: 'General Purpose Chatbot',
    description: 'Chatbot AI đa năng hỗ trợ khách hàng và nhân viên 24/7',
    icon: Brain,
    iconBg: 'bg-indigo-500',
    capabilities: [
      'Trả lời câu hỏi tự động',
      'Hỗ trợ đa ngôn ngữ',
      'Tích hợp Knowledge Base',
      'Học hỏi từ hội thoại',
      'Chuyển giao cho con người'
    ],
    source: 'System',
    status: 'deployed'
  },
  {
    id: 14,
    module: 'general',
    name: 'Trợ lý Phân tích Dữ liệu',
    nameEn: 'Data Analysis Agent',
    description: 'Phân tích dữ liệu tự động và tạo báo cáo thông minh',
    icon: TrendingUp,
    iconBg: 'bg-indigo-500',
    capabilities: [
      'Phân tích dữ liệu tự động',
      'Tạo dashboard trực quan',
      'Phát hiện xu hướng',
      'Dự báo thống kê',
      'Báo cáo theo yêu cầu'
    ],
    source: 'System',
    status: 'active'
  }
])

// Filter state
const searchQuery = ref('')
const statusFilter = ref('')
const sourceFilter = ref('')

const router = useRouter()
const showByProduct = ref(false) // Default: show by module
const selectedProduct = ref('dbiz-erp')
const selectedModule = ref('') // Default: show all agents (empty = all)
const modulesContainer = ref(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)

// Load data from API
const loadData = async () => {
  try {
    isLoading.value = true
    
    // Load all data at once
    const response = await call('dbiz_ai_agent.api.ai_catalog.get_catalog')
    
    if (response.success) {
      // Only update if API returns data, otherwise keep hardcoded data
      if (response.data.products && response.data.products.length > 0) {
        products.value = response.data.products.map(p => ({
          ...p,
          icon: iconMap[p.icon] || Brain,
          // logo is already set from API (from icon field - Attach Image)
          // Keep fallback to hardcoded logos if logo is not available
          logo: p.logo || (
            p.product_code === 'dbiz-erp' ? dbizErpLogo :
            p.product_code === 'dbiz-cx' ? dbizCxLogo :
            p.product_code === 'dbiz-data' ? dbizDataLogo :
            p.product_code === 'dbiz-microsme' ? dbizMicrosmeLogo : null
          )
        }))
        
        // Auto-select first product if none selected (only if showByProduct is enabled)
        if (showByProduct.value && (!selectedProduct.value || !products.value.find(p => p.id === selectedProduct.value))) {
          selectedProduct.value = products.value[0]?.id || ''
        }
      }
      
      if (response.data.modules && response.data.modules.length > 0) {
        modules.value = response.data.modules.map(m => ({
          ...m,
          icon: iconMap[m.icon] || Brain
        }))
      }
      
      if (response.data.agents && response.data.agents.length > 0) {
        agents.value = response.data.agents.map(a => ({
          ...a,
          icon: iconMap[a.icon] || Brain
        }))
      }
      
      console.log('Loaded from API - Products:', products.value.length, 'Modules:', modules.value.length, 'Agents:', agents.value.length)
    }
  } catch (error) {
    console.error('Failed to load AI catalog:', error)
    console.log('Using hardcoded data - Products:', products.value.length, 'Modules:', modules.value.length, 'Agents:', agents.value.length)
  } finally {
    isLoading.value = false
  }
}

// Load data on mount
onMounted(() => {
  loadData()
  
  // Default: show all agents (no module selected)
  if (!showByProduct.value) {
    selectedModule.value = ''
  }
  
  // Check scroll buttons after modules load
  setTimeout(() => {
    checkScrollButtons()
  }, 100)
  
  // Add resize listener
  window.addEventListener('resize', checkScrollButtons)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScrollButtons)
})

// Scroll modules container
const scrollModules = (direction) => {
  if (!modulesContainer.value) return
  
  const scrollAmount = 200
  const currentScroll = modulesContainer.value.scrollLeft
  
  if (direction === 'left') {
    modulesContainer.value.scrollTo({
      left: currentScroll - scrollAmount,
      behavior: 'smooth'
    })
  } else {
    modulesContainer.value.scrollTo({
      left: currentScroll + scrollAmount,
      behavior: 'smooth'
    })
  }
  
  // Check buttons after scroll
  setTimeout(() => {
    checkScrollButtons()
  }, 300)
}

// Check if scroll buttons should be visible
const checkScrollButtons = () => {
  if (!modulesContainer.value) {
    canScrollLeft.value = false
    canScrollRight.value = false
    return
  }
  
  const { scrollLeft, scrollWidth, clientWidth } = modulesContainer.value
  
  canScrollLeft.value = scrollLeft > 0
  canScrollRight.value = scrollLeft < scrollWidth - clientWidth - 1
}

// Computed properties
const currentProduct = computed(() => {
  return products.value.find(p => p.id === selectedProduct.value) || products.value[0]
})

const currentProductModules = computed(() => {
  if (!showByProduct.value || !currentProduct.value) return []
  return modules.value.filter(m => currentProduct.value.modules.includes(m.id))
})

// Display modules based on view mode
const displayModules = computed(() => {
  if (showByProduct.value) {
    // Show modules filtered by selected product (without "all" option)
    return currentProductModules.value
  } else {
    // Show all modules including "all" option
    return modules.value
  }
})

// Display modules with dynamic count from agents
const displayModulesWithCount = computed(() => {
  const modulesToDisplay = displayModules.value
  
  return modulesToDisplay.map(module => {
    // Count agents for this module
    const agentCount = agents.value.filter(agent => agent.module === module.id).length
    
    return {
      ...module,
      count: agentCount
    }
  })
})

const currentModule = computed(() => {
  if (!selectedModule.value) return null
  return modules.value.find(m => m.id === selectedModule.value) || null
})

const filteredAgents = computed(() => {
  // If no module selected, show all agents
  if (!selectedModule.value) {
    let result = [...agents.value]
    
    // If showing by product, filter by product
    if (showByProduct.value && selectedProduct.value) {
      const product = products.value.find(p => p.id === selectedProduct.value)
      if (product && product.modules) {
        result = result.filter(agent => 
          product.modules.includes(agent.module)
        )
      }
    }
    
    return result
  }
  
  // Filter by selected module
  let result = agents.value.filter(agent => agent.module === selectedModule.value)
  
  // If showing by product, also filter by product
  if (showByProduct.value && selectedProduct.value) {
    const product = products.value.find(p => p.id === selectedProduct.value)
    if (product && product.modules) {
      // Only show agents if the module belongs to the selected product
      if (!product.modules.includes(selectedModule.value)) {
        return []
      }
    }
  }
  
  return result
})

// Final filtered agents with search and filters
const finalFilteredAgents = computed(() => {
  let result = filteredAgents.value

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(agent => 
      agent.name.toLowerCase().includes(query) ||
      agent.nameEn.toLowerCase().includes(query) ||
      agent.description.toLowerCase().includes(query) ||
      agent.capabilities.some(cap => cap.toLowerCase().includes(query))
    )
  }

  // Status filter
  if (statusFilter.value) {
    result = result.filter(agent => agent.status === statusFilter.value)
  }

  // Source filter
  if (sourceFilter.value) {
    result = result.filter(agent => agent.source === sourceFilter.value)
  }

  return result
})

// Check if has active filters
const hasActiveFilters = computed(() => {
  return searchQuery.value.trim() !== '' || statusFilter.value !== '' || sourceFilter.value !== ''
})

// Clear all filters
const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  sourceFilter.value = ''
}

// View agent details
const viewAgentDetails = (agent) => {
  // Navigate to agent details page using agent DocType name
  const agentId = agent.docName || agent.name || agent.id
  router.push({
    name: 'AgentDetail',
    params: { id: agentId }
  })
}

// Handle image error
const handleImageError = (event) => {
  // Hide broken image
  event.target.style.display = 'none'
}

// Auto-select first module when product changes (only if showByProduct is true)
watch(selectedProduct, (newProduct) => {
  if (!showByProduct.value) return
  
  console.log('Product changed to:', newProduct)
  const currentModules = modules.value.filter(m => 
    products.value.find(p => p.id === newProduct)?.modules.includes(m.id)
  )
  console.log('Current modules:', currentModules.map(m => m.id))
  if (currentModules.length > 0) {
    selectedModule.value = currentModules[0].id
    console.log('Auto-selected module:', selectedModule.value)
  } else {
    selectedModule.value = ''
  }
  // Clear filters when product changes
  clearFilters()
}, { immediate: false })

// Reset module selection when switching view modes
watch(showByProduct, (newValue) => {
  if (!newValue) {
    // When switching to module view, show all agents (no module selected)
    selectedModule.value = ''
  } else {
    // When switching to product view, auto-select first module of selected product
    if (selectedProduct.value) {
      const currentModules = modules.value.filter(m => 
        products.value.find(p => p.id === selectedProduct.value)?.modules.includes(m.id)
      )
      if (currentModules.length > 0) {
        selectedModule.value = currentModules[0].id
      } else {
        selectedModule.value = ''
      }
    }
  }
  clearFilters()
})

// Clear filters when module changes
watch(selectedModule, (newValue) => {
  console.log('Module changed to:', newValue)
  console.log('Filtered agents:', filteredAgents.value.length)
  clearFilters()
})

// Watch for modules changes to update scroll buttons
watch(displayModules, () => {
  setTimeout(() => {
    checkScrollButtons()
  }, 100)
})
</script>

<style scoped>
/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hide scrollbar for horizontal scroll */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}

.scrollbar-hide::-webkit-scrollbar {
  height: 6px;
}

.scrollbar-hide::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-hide::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.scrollbar-hide::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* 3D Product Card Effect - Square corners, strong 3D */
.product-card-3d {
  transform-style: preserve-3d;
  perspective: 1000px;
  position: relative;
  border-width: 3px !important;
}

.product-card-3d::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 40%, rgba(0, 0, 0, 0.08) 100%);
  pointer-events: none;
  z-index: 1;
}

.product-card-3d::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid rgba(255, 255, 255, 0.3);
  pointer-events: none;
  z-index: 2;
}

.product-card-selected {
  box-shadow: 
    0 20px 40px -10px rgba(59, 130, 246, 0.4),
    0 15px 25px -10px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(59, 130, 246, 0.2),
    inset 0 2px 4px rgba(255, 255, 255, 0.9),
    inset 0 -2px 4px rgba(0, 0, 0, 0.1),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-3px) scale(1.03);
  border-color: #3b82f6;
}

.product-card-3d:not(.product-card-selected) {
  box-shadow: 
    0 8px 16px -4px rgba(0, 0, 0, 0.2),
    0 4px 8px -2px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(0, 0, 0, 0.1),
    inset 0 2px 4px rgba(255, 255, 255, 0.9),
    inset 0 -2px 4px rgba(0, 0, 0, 0.08),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.1);
}

.product-card-3d:hover:not(.product-card-selected) {
  box-shadow: 
    0 15px 30px -5px rgba(0, 0, 0, 0.25),
    0 8px 16px -4px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(59, 130, 246, 0.3),
    inset 0 2px 4px rgba(255, 255, 255, 0.9),
    inset 0 -2px 4px rgba(0, 0, 0, 0.1),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

/* Full Frame Logo - Square corners, no border radius */
.product-logo-full-frame {
  position: relative;
  overflow: hidden;
}

.product-logo-full-frame::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 45%, rgba(0, 0, 0, 0.1) 100%);
  pointer-events: none;
  z-index: 1;
}

.product-card-selected .product-logo-full-frame::before {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, transparent 45%, rgba(59, 130, 246, 0.08) 100%);
}

/* Module Card 3D Effect - Matching product cards style */
.module-card-3d {
  transform-style: preserve-3d;
  position: relative;
  border-width: 2px !important;
}

.module-card-3d::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 40%, rgba(0, 0, 0, 0.05) 100%);
  pointer-events: none;
  z-index: 1;
}

.module-card-selected {
  box-shadow: 
    0 12px 24px -6px rgba(59, 130, 246, 0.3),
    0 8px 16px -4px rgba(59, 130, 246, 0.2),
    0 0 0 1px rgba(59, 130, 246, 0.2),
    inset 0 1px 2px rgba(255, 255, 255, 0.9),
    inset 0 -1px 2px rgba(0, 0, 0, 0.08),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.08);
  transform: translateY(-1px) scale(1.02);
  border-color: #3b82f6;
}

.module-card-3d:not(.module-card-selected) {
  box-shadow: 
    0 4px 8px -2px rgba(0, 0, 0, 0.15),
    0 2px 4px -1px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(0, 0, 0, 0.08),
    inset 0 1px 2px rgba(255, 255, 255, 0.9),
    inset 0 -1px 2px rgba(0, 0, 0, 0.06),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.08);
}

.module-card-3d:hover:not(.module-card-selected) {
  box-shadow: 
    0 8px 16px -4px rgba(0, 0, 0, 0.2),
    0 4px 8px -2px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(59, 130, 246, 0.25),
    inset 0 1px 2px rgba(255, 255, 255, 0.9),
    inset 0 -1px 2px rgba(0, 0, 0, 0.08),
    inset 1px 1px 0 rgba(255, 255, 255, 0.8),
    inset -1px -1px 0 rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

/* Module Icon Frame */
.module-icon-frame {
  position: relative;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  box-shadow: 
    inset 0 1px 2px rgba(0, 0, 0, 0.05),
    0 1px 2px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.module-icon-selected {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  box-shadow: 
    inset 0 1px 2px rgba(59, 130, 246, 0.15),
    0 1px 2px rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

/* Module Scroll Buttons */
.module-scroll-btn {
  backdrop-filter: blur(4px);
}

.module-scroll-btn:hover {
  transform: scale(1.1);
}
</style>