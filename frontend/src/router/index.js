import { createRouter, createWebHistory } from "vue-router";
import Home from "../Components/Home.vue";
import NmapView from "../Components/Nmap.vue";
import NiktoView from "../Components/Nikto.vue";
import GobusterView from "../Components/Gobuster.vue";
import CurlView from "../Components/Curl.vue";
import SqlmapView from "../Components/Sqlmap.vue";
import HydraView from "../Components/Hydra.vue";

const routes = [
    { path: "/", name: "home", component: Home },
    { path: "/commands/nmap", name: "nmap", component: NmapView },
    { path: "/commands/nikto", name: "nikto", component: NiktoView },
    { path: "/commands/gobuster", name: "gobuster", component: GobusterView },
    { path: "/commands/curl", name: "curl", component: CurlView },
    { path: "/commands/sqlmap", name: "sqlmap", component: SqlmapView },
    { path: "/commands/hydra", name: "hydra", component: HydraView },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;