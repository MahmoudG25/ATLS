# ⚙️ SYSTEM CORE: SUPERADMIN CONTROLS & FEATURE TOGGLE LOGIC
# Architecture: Tenant-Aware Feature Flags & Presentational Segregation
# Target Server: Django (PostgreSQL) + React (RTL, 100% Responsive)

---

## 🏁 CHECKPOINT 1: BACK-END SCHEMA & FEATURE FLAGS

### 📋 Step 1.1: Database Model Augmentation
File: `apps/users/models.py` (or equivalent config models file)
Create the configuration schema to store dynamic runtime application toggles and system branding assets per farm/tenant.

```python
import uuid
from django.db import models
from core.models import TenantAwareModel

class FarmSystemConfig(TenantAwareModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Branding Specs
    farm_name = models.CharField(max_length=255, default="مزرعة أطلس النموذجية")
    logo_url = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=50, default="#1E3A1E") # Deep Academic Green
    accent_color = models.CharField(max_length=50, default="#D4AF37")  # Wheat Gold
    currency = models.CharField(max_length=20, default="جنية مصري")
    active_font = models.CharField(max_length=50, default="Cairo")
    
    # Feature Toggles (Global Application Flags)
    feature_accounting = models.BooleanField(default=True, verbose_name="نظام المحاسبة")
    feature_hr = models.BooleanField(default=True, verbose_name="نظام الموارد البشرية HR")
    feature_fleet = models.BooleanField(default=True, verbose_name="منظومة الأسطول والمعدات")
    feature_warehouse = models.BooleanField(default=True, verbose_name="إدارة المخازن والمستودع")

    class Meta:
        db_table = 'farm_system_configs'
        verbose_name = 'إعدادات النظام والمزرعة'
📋 Step 1.2: Serializers and Views Formulation
Create the DRF endpoints to allow the Super Admin to fetch and update these configurations.

File: api/endpoints/admin_data_views.py (or create if not exists)

Python
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from apps.users.models import FarmSystemConfig

class FarmSystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmSystemConfig
        fields = '__all__'
        read_only_fields = ['id', 'company']

class FarmSystemConfigView(generics.RetrieveUpdateAPIView):
    serializer_class = FarmSystemConfigSerializer
    permission_classes = [IsAuthenticated] # Ensure custom super-admin permission is checked if needed

    def get_object(self):
        # Always return the configuration for the current user's tenant
        obj, created = FarmSystemConfig.objects.get_or_create(company=self.request.user.company)
        return obj
File: api/urls.py

Python
# Add this to urlpatterns:
# path('admin/config/', admin_data_views.FarmSystemConfigView.as_view(), name='farm-config'),
🏁 CHECKPOINT 2: GLOBAL FRONT-END CONFIGURATION CONTEXT
📋 Step 2.1: Establish FeatureToggleContext.jsx
File location: src/contexts/FeatureToggleContext.jsx.
This component fetches the real config from the backend on load and injects the CSS variables globally.

JavaScript
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '@/services/api'; // Ensure correct path to your axios instance

const FeatureToggleContext = createContext(null);

export function FeatureToggleProvider({ children }) {
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.get('/admin/config/');
        const data = response.data;
        
        // Map backend data to frontend structure
        const mappedConfig = {
          branding: {
            farm_name: data.farm_name,
            primary_color: data.primary_color,
            accent_color: data.accent_color,
            font: data.active_font,
            currency: data.currency
          },
          features: {
            accounting: data.feature_accounting,
            hr: data.feature_hr,
            fleet: data.feature_fleet,
            warehouse: data.feature_warehouse
          }
        };
        setConfig(mappedConfig);
      } catch (error) {
        console.error("Failed to load system config, using fallbacks.", error);
        // Fallback default config
        setConfig({
          branding: { farm_name: "مزرعة أطلس النموذجية", primary_color: "#1E3A1E", accent_color: "#D4AF37", font: "Cairo", currency: "جنية" },
          features: { accounting: true, hr: true, fleet: true, warehouse: true }
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchConfig();
  }, []);

  // Inject Custom Tailwind Themes on runtime configuration synchronization
  useEffect(() => {
    if (config) {
      const root = document.documentElement;
      root.style.setProperty('--primary-farm', config.branding.primary_color);
      root.style.setProperty('--accent-farm', config.branding.accent_color);
      root.style.fontFamily = `${config.branding.font}, sans-serif`;
    }
  }, [config]);

  if (isLoading) return <div className="flex h-screen items-center justify-center text-emerald-900 font-bold">جاري تحميل إعدادات النظام...</div>;

  return (
    <FeatureToggleContext.Provider value={{ config, setConfig }}>
      {children}
    </FeatureToggleContext.Provider>
  );
}

export const useFeatures = () => useContext(FeatureToggleContext);
🏁 CHECKPOINT 3: CONDITIONAL ROUTE INTERCEPTORS
📋 Step 3.1: Define FeatureGuard Component
File: src/routes/FeatureGuard.jsx

JavaScript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useFeatures } from '@/contexts/FeatureToggleContext';

export default function FeatureGuard({ featureKey, children }) {
  const { config } = useFeatures();
  
  if (!config || !config.features[featureKey]) {
    // If feature is disabled, redirect to dashboard silently without breaking
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
}
📋 Step 3.2: Apply Guards in AppRoutes.jsx
File: src/routes/AppRoutes.jsx
Ensure that your main routes are wrapped. Example mapping:

JavaScript
// Import the guard
// import FeatureGuard from './FeatureGuard';

// Wrap specific routes:
// <Route path="/accounting/*" element={
//    <FeatureGuard featureKey="accounting">
//        <FinanceDashboard />
//    </FeatureGuard>
// } />