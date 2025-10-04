# Frontend API URL Migration Guide

## Files Updated

### ✅ Completed:

1. `src/lib/api-config.ts` - Created centralized API configuration
2. `src/app/page.tsx` - Updated to use API_BASE_URL
3. `src/components/hierarchy-tree.tsx` - Updated to use getApiUrl()

### 🔄 Remaining Files (Quick Reference):

All remaining files need to:

1. Import: `import { getApiUrl } from "@/lib/api-config";` or `import { API_BASE_URL } from "@/lib/api-config";`
2. Replace: `"http://localhost:8000/..."` with `getApiUrl("/...")`

#### Files to Update:

- `src/components/ai-chat.tsx` - Line 85
- `src/components/auto-suggestions.tsx` - Lines 43-44, 67, 127, 143
- `src/components/detail-panel.tsx` - Lines 94-95
- `src/app/components/casevac-builder.tsx` - Lines 74, 114
- `src/app/components/eoincrep-builder.tsx` - Lines 80, 118

## Testing Checklist

After deployment:

- [ ] Frontend connects to backend API
- [ ] Hierarchy tree loads
- [ ] Reports display correctly
- [ ] AI chat functions
- [ ] Suggestions load
- [ ] FRAGO, CASEVAC, EOINCREP builders work

## Environment Variables

### Local Development (.env.local):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Render auto-sets):

```
NEXT_PUBLIC_API_URL=https://military-hierarchy-backend-xxxx.onrender.com
```

## How It Works

The `api-config.ts` automatically detects the environment:

- **Local**: Uses `http://localhost:8000` (default)
- **Production**: Uses `process.env.NEXT_PUBLIC_API_URL` from Render

No code changes needed between environments! 🎉
