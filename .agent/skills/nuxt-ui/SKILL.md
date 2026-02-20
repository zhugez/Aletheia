---
name: nuxt-ui
description: >
  Build modern Vue/Nuxt applications with Nuxt UI — a comprehensive component library powered
  by Radix Vue and Tailwind CSS v4. Covers installation, theming, component usage, and
  form patterns for Nuxt 3 applications.
  Use when: nuxt ui, vue components, nuxt components, radix vue, nuxt design system.
---

# Nuxt UI Skill

> A UI Library for Modern Web Apps — fully styled, accessible components for Nuxt 3 powered by Radix Vue and Tailwind CSS v4.

## When to Use

- Building Nuxt 3 applications that need production-ready UI components
- Creating Vue.js interfaces with accessible, well-designed components
- Setting up a design system for Nuxt projects
- Need components with built-in dark mode, keyboard navigation, and responsive design

## Setup

### Installation

```bash
npx nuxi@latest module add ui
```

### Configuration

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxt/ui'],
})
```

### Tailwind CSS v4

Nuxt UI v3 uses Tailwind CSS v4. Import the theme in your CSS:

```css
/* assets/css/main.css */
@import "tailwindcss";
@import "@nuxt/ui";
```

## Key Components

### 1. Buttons

```vue
<template>
  <UButton label="Click me" />
  <UButton label="Danger" color="red" variant="soft" />
  <UButton label="Loading..." loading />
  <UButton icon="i-lucide-plus" size="sm" />
</template>
```

### 2. Forms

```vue
<template>
  <UForm :schema="schema" :state="state" @submit="onSubmit">
    <UFormField label="Email" name="email">
      <UInput v-model="state.email" type="email" />
    </UFormField>
    <UFormField label="Password" name="password">
      <UInput v-model="state.password" type="password" />
    </UFormField>
    <UButton type="submit" label="Submit" />
  </UForm>
</template>

<script setup lang="ts">
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
})

const state = reactive({ email: '', password: '' })
const onSubmit = () => console.log(state)
</script>
```

### 3. Data Table

```vue
<template>
  <UTable :data="users" :columns="columns" />
</template>

<script setup>
const columns = [
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'email', header: 'Email' },
  { accessorKey: 'role', header: 'Role' },
]

const users = [
  { name: 'John', email: 'john@example.com', role: 'Admin' },
]
</script>
```

### 4. Navigation — CommandPalette

```vue
<template>
  <UCommandPalette :groups="groups" />
</template>

<script setup>
const groups = [{
  key: 'actions',
  label: 'Actions',
  commands: [
    { id: 'new', label: 'New file', icon: 'i-lucide-file-plus' },
    { id: 'search', label: 'Search', icon: 'i-lucide-search' },
  ]
}]
</script>
```

## Theming

### App Config

```ts
// app.config.ts
export default defineAppConfig({
  ui: {
    colors: {
      primary: 'green',
      neutral: 'slate',
    },
  },
})
```

### Dark Mode

Dark mode works out of the box with `@nuxtjs/color-mode`:

```vue
<template>
  <UButton
    :icon="isDark ? 'i-lucide-sun' : 'i-lucide-moon'"
    @click="isDark = !isDark"
  />
</template>

<script setup>
const colorMode = useColorMode()
const isDark = computed({
  get: () => colorMode.value === 'dark',
  set: () => colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark',
})
</script>
```

## Best Practices

1. **Use app.config.ts for theming** — Not nuxt.config.ts
2. **Leverage built-in icons** — Use Lucide icons via `i-lucide-*` pattern
3. **Form validation** — Always pair `UForm` with Zod or Yup schemas
4. **Responsive design** — Components are responsive by default; use Tailwind breakpoints for layout

## References

- [Nuxt UI Documentation](https://ui.nuxt.com)
- [Nuxt UI GitHub](https://github.com/nuxt/ui)
- [Radix Vue](https://www.radix-vue.com)
