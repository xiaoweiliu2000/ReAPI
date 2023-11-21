import { createRouter, createWebHashHistory } from 'vue-router'

// 导入组件
import ReapiHome from "../components/ReapiHome.vue"
import NotFound from "../components/NotFound.vue"
import ApiHub from "../components/ApiHub.vue"
import MashupHub from "../components/MashupHub.vue"
import KnowledgeHub from "../components/KnowledgeHub.vue"
import EasyMashup from "../components/EasyMashup.vue"
import OpenAPI from "../components/OpenAPI.vue"
import ApiInfo from "../components/ApiInfo.vue"
import MashupInfo from "../components/MashupInfo.vue"

//创建并暴露一个router
const router = createRouter({
    history: createWebHashHistory(),
    routes:[
        {
            path:'/home',
            component:ReapiHome,
            meta: {
                title:'ReAPI - Home'
            }
        },
        {
            path:'/apihub',
            component:ApiHub,
            meta: {
                title:'ReAPI - API Hub'
            }
        },
        {
            path:'/mashuphub',
            component:MashupHub,
            meta: {
                title:'ReAPI - Mashup Hub',
            }
        },
        {
            path:'/knowledge',
            component:KnowledgeHub,
            meta: {
                title:'ReAPI - Knowledge'
            }
        },
        {
            path:'/knowledge/:id',
            component:KnowledgeHub,
            props: true,
            meta: {
                title:'ReAPI - Knowledge'
            }
        },
        {
            path:'/easymashup',
            component:EasyMashup,
            meta: {
                title:'ReAPI - EasyMashup'
            }
        },
        {
            path:'/openapi',
            component:OpenAPI,
            meta: {
                title:'ReAPI - Open API'
            }
        },
        {
            path:'/api/:id',
            component:ApiInfo,
            props: true,
            meta: {
                title:'ReAPI - API Profile'
            }
        },
        {
            path:'/mashup/:id',
            component:MashupInfo,
            props: true,
            meta: {
                title:'ReAPI - Mashup Profile'
            }
        },
        {
            path:'',
            redirect:'/home'
        },
        {
            path:'/404',
            component:NotFound
        },
        {
            path:'/:path(.*)',
            redirect:'/404'
        },
    ]
})


router.beforeEach((to, from, next) =>{
    window.document.title = to.meta.title
    next()
})

export default router
