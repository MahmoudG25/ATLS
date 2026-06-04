# 🎨 FILE 2: FRONT-END UI/UX STITCH UNIFICATION SPECIFICATION
# Protocol: Pure Presentational & Container Architecture Unification
# Theme Aesthetic: Minimalist Academic Green (#1E3A1E) & Wheat Gold (#D4AF37)
# Language & Direction: Arabic (RTL) / 100% Responsive Layout Guardrails

---

## 🏁 CHECKPOINT 4: PURE STITCH VIEW DEFINITIONS (STATELESS PRESENTATION)

### 📋 Step 4.1: Create Presentational Layout Directory
Create a dedicated sub-folder at `src/components/ui_stitches/` to house all pure presentational visual layouts generated from `stitch.withgoogle.com`. These components must be 100% stateless and must only receive data and handlers via strict React `props`.

### 💻 Step 4.2: Implement `SuperAdminDashboardView.jsx`
Create file `src/components/ui_stitches/SuperAdminDashboardView.jsx` containing the sanitized HTML/Tailwind wireframe from Stitch:

```jsx
import React from 'react';
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sliders, Palette, ShieldAlert } from "lucide-react";

export default function SuperAdminDashboardView({ 
  brandingData, 
  featureFlags, 
  onToggleFeature, 
  onSaveBranding,
  onInputChange,
  isSaving
}) {
  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-6 text-right font-sans" dir="rtl">
      {/* Top Header Branding Banner */}
      <div className="flex flex-col space-y-1 border-b border-slate-200/60 pb-4">
        <div className="flex items-center space-x-reverse space-x-2 text-emerald-900">
          <Sliders className="h-6 w-6 text-[var(--primary-farm)]" />
          <h1 className="text-2xl font-bold tracking-tight">لوحة تحكم وتخصيص السوبر أدمن (SaaS Mode)</h1>
        </div>
        <p className="text-xs text-slate-500">
          تخصيص الهوية البصرية، إعدادات الخطوط والثيمات، والتحكم المطلق في تشغيل وإيقاف وحدات النظام ديناميكياً.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1 & 2: Branding Specs & Layout Design */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-slate-200 shadow-sm bg-white overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100 p-4">
              <CardTitle className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Palette className="h-4 w-4 text-emerald-700" /> الهوية البصرية المخصصة والسمات الملكية
              </CardTitle>
              <CardDescription className="text-[11px]">تحديث شعار وألوان خطوط النظام فورياً للمزرعة الحالية.</CardDescription>
            </CardHeader>
            <CardContent className="p-5 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600">اسم المنشأة / المزرعة التجاري</label>
                  <Input 
                    value={brandingData.farm_name} 
                    onChange={(e) => onInputChange('farm_name', e.target.value)}
                    className="text-xs focus-visible:ring-emerald-800 h-10" 
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600">العملة المعتمدة في المعاملات</label>
                  <Input 
                    value={brandingData.currency} 
                    onChange={(e) => onInputChange('currency', e.target.value)}
                    className="text-xs h-10" 
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600">اللون الأساسي (Primary)</label>
                  <div className="flex gap-2">
                    <Input 
                      type="color" 
                      value={brandingData.primary_color} 
                      onChange={(e) => onInputChange('primary_color', e.target.value)}
                      className="w-12 h-10 p-1 cursor-pointer rounded-lg" 
                    />
                    <Input value={brandingData.primary_color} readOnly className="text-xs h-10 bg-slate-50" />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600">اللون الثانوي (Accent)</label>
                  <div className="flex gap-2">
                    <Input 
                      type="color" 
                      value={brandingData.accent_color} 
                      onChange={(e) => onInputChange('accent_color', e.target.value)}
                      className="w-12 h-10 p-1 cursor-pointer rounded-lg" 
                    />
                    <Input value={brandingData.accent_color} readOnly className="text-xs h-10 bg-slate-50" />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-600">نوع خط الكتابة المتناسق</label>
                  <Select value={brandingData.font} onValueChange={(val) => onInputChange('font', val)}>
                    <SelectTrigger className="h-10 text-xs"><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Cairo">Cairo (خط عربي نقي)</SelectItem>
                      <SelectItem value="Tajawal">Tajawal (عصري نحيف)</SelectItem>
                      <SelectItem value="Montserrat">Montserrat (للانجليزية)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="border-t pt-4 flex justify-end">
                <Button 
                  className="bg-emerald-800 hover:bg-emerald-900 text-white text-xs h-9 px-6 font-bold rounded-lg shadow-sm"
                  onClick={onSaveBranding}
                  disabled={isSaving}
                >
                  {isSaving ? "جاري حفظ التغييرات..." : "حفظ وتطبيق الهوية البصرية البنائية 💾"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Column 3: Feature Toggles App Controllers */}
        <div className="space-y-6">
          <Card className="border-slate-200 shadow-sm bg-white overflow-hidden">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100 p-4">
              <CardTitle className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-amber-600" /> تفعيل وإيقاف موديولات النظام (Feature Flags)
              </CardTitle>
              <CardDescription className="text-[11px]">تعطيل أي جزء يخفيه تماماً من القوائم والتقارير دون أي كسر.</CardDescription>
            </CardHeader>
            <CardContent className="p-4 space-y-3.5">
              {[
                { key: 'accounting', title: 'المنظومة المالية والحسابات', desc: 'إخفاء شاشات الدفاتر المحاسبية وفواتير المزرعة.' },
                { key: 'hr', title: 'إدارة الموارد البشرية والـ HR', desc: 'حظر كروت حضور الموظفين ومستندات رواتب العمال.' },
                { key: 'fleet', title: 'أسطول الحركة والمعدات الآلية', desc: 'تعطيل عدادات تشغيل الجرارات والسيارات الوقائية.' },
                { key: 'warehouse', title: 'المستودعات وحركات المخازن', desc: 'قفل تتبع المواد والأسمدة الحالية والعهد.' }
              ].map(item => (
                <div key={item.key} className="flex items-center justify-between p-3 border rounded-xl bg-slate-50/40 border-slate-100 hover:bg-slate-50 transition-colors">
                  <div className="space-y-0.5 ml-4">
                    <span className="text-xs font-bold text-slate-800 block">{item.title}</span>
                    <span className="text-[10px] text-slate-400 block">{item.desc}</span>
                  </div>
                  <Switch 
                    checked={featureFlags[item.key]} 
                    onCheckedChange={(checked) => onToggleFeature(item.key, checked)} 
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
🏁 CHECKPOINT 5: STATE CONTROLLERS & DATA CONTAINERS MAPPING
🎛️ Step 5.1: Implement Functional Container Parent with REAL API calls
Create src/pages/admin/AdminControls.jsx. This component acts as the data fetcher/handler container which loads data, updates the backend via axios/api, and mounts our stateless Stitch view via props.

JavaScript
import React, { useState, useEffect } from 'react';
import SuperAdminDashboardView from "@/components/ui_stitches/SuperAdminDashboardView";
import { useFeatures } from "@/contexts/FeatureToggleContext";
import api from "@/services/api"; // Ensure Axios is imported

export default function AdminControls() {
  const { config, setConfig } = useFeatures();
  const [brandingData, setBrandingData] = useState({ ...config.branding });
  const [featureFlags, setFeatureFlags] = useState({ ...config.features });
  const [isSaving, setIsSaving] = useState(false);

  const handleInputChange = (field, value) => {
    setBrandingData(prev => ({ ...prev, [field]: value }));
  };

  const handleToggleFeature = async (featureKey, isEnabled) => {
    // 1. Optimistic UI update
    const updatedFeatures = { ...featureFlags, [featureKey]: isEnabled };
    setFeatureFlags(updatedFeatures);
    setConfig(prev => ({ ...prev, features: updatedFeatures }));
    
    // 2. Persist to Backend immediately
    try {
      // Map frontend key to backend model field name
      const payloadKey = `feature_${featureKey}`;
      await api.patch('/admin/config/', { [payloadKey]: isEnabled });
    } catch (error) {
      console.error("Failed to persist feature toggle.", error);
      // Revert state if failed (optional, depending on UX preference)
    }
  };

  const handleSaveBranding = async () => {
    setIsSaving(true);
    try {
      // Map frontend keys to match DRF Serializer fields
      const payload = {
        farm_name: brandingData.farm_name,
        primary_color: brandingData.primary_color,
        accent_color: brandingData.accent_color,
        active_font: brandingData.font,
        currency: brandingData.currency
      };
      
      await api.patch('/admin/config/', payload);
      setConfig(prev => ({ ...prev, branding: brandingData }));
      // Optional: Trigger success toast notification here
    } catch (error) {
      console.error("Failed syncing branding options.", error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SuperAdminDashboardView 
      brandingData={brandingData}
      featureFlags={featureFlags}
      onToggleFeature={handleToggleFeature}
      onSaveBranding={handleSaveBranding}
      onInputChange={handleInputChange}
      isSaving={isSaving}
    />
  );
}
🏁 CHECKPOINT 6: CONDITIONAL VISIBILITY IN SIDEBAR NAVIGATION
📑 Step 6.1: Update src/layouts/DashboardLayout.jsx
Ensure that the navigation array maps the visible property based on the Context, and filter the items before rendering.

JavaScript
// Explicit update rule inside side navigation array block loops:
import { useFeatures } from "@/contexts/FeatureToggleContext";

// Inside the component:
const { config } = useFeatures();

const navigationItems = [
  { path: '/dashboard', label: 'الرئيسية', icon: Home, visible: true },
  { path: '/accounting', label: 'الحسابات', icon: DollarSign, visible: config.features.accounting },
  { path: '/hr', label: 'الموارد البشرية', icon: Users, visible: config.features.hr },
  { path: '/equipment', label: 'المعدات والأسطول', icon: Truck, visible: config.features.fleet },
  { path: '/warehouse', label: 'المستودعات', icon: Warehouse, visible: config.features.warehouse },
  { path: '/admin-controls', label: 'لوحة السوبر أدمن', icon: Settings, visible: true, superAdminOnly: true },
];

// In the render return:
// {navigationItems.filter(item => item.visible).map(item => ( ... ))}
🏁 CHECKPOINT 7: INTERCEPT COMPONENT FIELDS IN OTHER SHORELINES
If a feature like HR or Warehouse is toggled off, fields in reporting modules must naturally drop out without throw arguments.

🌾 Step 7.1: Conditional injection rules inside DailyTaskForm.jsx or specialized reports:
JavaScript
import { useFeatures } from "@/contexts/FeatureToggleContext";

// Inside the form render:
// {config.features.hr && (
//   <div className="hr-labor-allocation-block animate-in fade-in">
//      {/* Existing Labor input modules code here */}
//   </div>
// )}