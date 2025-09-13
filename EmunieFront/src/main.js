import { createApp } from 'vue'
import App from './Header.vue'

// PrimeVue (avec thème Aura)
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'

// Composants
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'



// App
const app = createApp(App)

app.use(PrimeVue, {
  theme: {
    preset: Aura
  }
})

app.component('Button', Button)
app.component('InputText', InputText)


app.mount('#app')
