// Metadata cho menu chính (Main Menu)
import {
    Home as HomeIcon,
    Brain as BrainIcon,
    MessageSquare as MessageSquareIcon,
    BookOpen as BookOpenIcon,
    // ScanText as ScanTextIcon, // Đã ẩn menu OCR
    Link as LinkIcon,
    BarChart as BarChartIcon,
    Shield as ShieldIcon,
    Settings as SettingsIcon,
    User as UserIcon
} from 'lucide-vue-next'

export const mainMenu = [
    {
        path: '/',
        label: 'common.dashboard',
        icon: HomeIcon,
        titleKey: 'sidebar.menuItems.dashboard.title',
        descriptionKey: 'sidebar.menuItems.dashboard.description',
    },
    {
        path: '/ai-agents',
        label: 'common.aiAgents',
        icon: BrainIcon,
        titleKey: 'sidebar.menuItems.aiAgents.title',
        descriptionKey: 'sidebar.menuItems.aiAgents.description',
    },
    // Ẩn menu Xử lý chứng từ tự động
    // {
    //     path: '/ocr',
    //     label: 'common.ocr',
    //     icon: ScanTextIcon,
    //     titleKey: 'sidebar.menuItems.ocr.title',
    //     descriptionKey: 'sidebar.menuItems.ocr.description',
    // },
    {
        path: '/knowledge',
        label: 'common.knowledge',
        icon: BookOpenIcon,
        titleKey: 'sidebar.menuItems.knowledge.title',
        descriptionKey: 'sidebar.menuItems.knowledge.description',
    },
    {
        path: '/integrations',
        label: 'common.integrations',
        icon: LinkIcon,
        titleKey: 'sidebar.menuItems.integrations.title',
        descriptionKey: 'sidebar.menuItems.integrations.description',
    },
    {
        path: '/analytics',
        label: 'common.analytics',
        icon: BarChartIcon,
        titleKey: 'sidebar.menuItems.analytics.title',
        descriptionKey: 'sidebar.menuItems.analytics.description',
    },
    {
        path: '/permissions',
        label: 'common.permissions',
        icon: ShieldIcon,
        titleKey: 'sidebar.menuItems.permissions.title',
        descriptionKey: 'sidebar.menuItems.permissions.description',
    },
]

// Metadata cho menu hệ thống (System)
export const systemMenu = [
    {
        path: '/settings',
        label: 'common.settings',
        icon: SettingsIcon,
        titleKey: 'sidebar.menuItems.settings.title',
        descriptionKey: 'sidebar.menuItems.settings.description',
    },
    {
        path: '/profile',
        label: 'common.profile',
        icon: UserIcon,
        titleKey: 'sidebar.menuItems.profile.title',
        descriptionKey: 'sidebar.menuItems.profile.description',
    },
]
