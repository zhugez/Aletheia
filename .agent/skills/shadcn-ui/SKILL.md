---
name: shadcn-ui
description: >
  Build beautiful, accessible React UIs with shadcn/ui — a collection of reusable components
  built on Radix UI and styled with Tailwind CSS. Covers installation, theming, component
  customization, and design system integration.
  Use when: shadcn, shadcn/ui, radix ui components, tailwind components, accessible react UI.
---

# shadcn/ui Skill

> Beautiful, accessible React components you own and customize. Not a component library — copy/paste components you control.

## When to Use

- Building React/Next.js UIs that need accessible, well-designed components
- Setting up a design system with Tailwind CSS
- Customizing UI components beyond what traditional libraries allow
- Creating forms, dialogs, data tables, and navigation
- Need Radix UI primitives with Tailwind styling out of the box

## Core Philosophy

shadcn/ui is **NOT a dependency** — it's a collection of reusable components you copy into your project. You own the code. You customize it. No npm package to update.

## Setup

### Next.js (Recommended)

```bash
npx shadcn@latest init
```

Configuration prompts:
- **Style**: Default or New York
- **Base color**: Slate, Gray, Zinc, Neutral, or Stone
- **CSS variables**: Yes (recommended)

### Adding Components

```bash
# Add individual components
npx shadcn@latest add button
npx shadcn@latest add dialog
npx shadcn@latest add form

# Add multiple at once
npx shadcn@latest add button card input label
```

## Key Patterns

### 1. Button Variants

```tsx
import { Button } from "@/components/ui/button"

<Button variant="default">Primary</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>
```

### 2. Forms with Validation (React Hook Form + Zod)

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  username: z.string().min(2).max(50),
})

export function ProfileForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "" },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="Enter username" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

### 3. Data Table

```bash
npx shadcn@latest add table
```

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>John Doe</TableCell>
      <TableCell>Active</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### 4. Theming with CSS Variables

```css
/* globals.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
  }
}
```

## Best Practices

1. **Use the CLI** — Always use `npx shadcn@latest add` instead of manually copying files
2. **Customize via `cn()` utility** — Merge Tailwind classes cleanly
3. **Keep component structure** — Don't restructure the `ui/` directory
4. **Dark mode** — Use `next-themes` with shadcn's built-in dark mode support
5. **Consistent theming** — Modify CSS variables in `globals.css`, not individual components

## File Structure

```
components/
├── ui/              # shadcn components (auto-generated)
│   ├── button.tsx
│   ├── dialog.tsx
│   └── ...
├── your-components/ # Your custom components using shadcn primitives
│   └── user-nav.tsx
lib/
└── utils.ts         # cn() utility function
```

## References

- [shadcn/ui Documentation](https://ui.shadcn.com)
- [shadcn/ui GitHub](https://github.com/shadcn-ui/ui)
- [Radix UI Primitives](https://www.radix-ui.com)
