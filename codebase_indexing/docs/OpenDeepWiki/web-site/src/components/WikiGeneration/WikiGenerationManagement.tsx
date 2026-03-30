// Wiki生成管理组件

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText } from 'lucide-react'

interface WikiGenerationManagementProps {
  warehouseId: string
}

const WikiGenerationManagement: React.FC<WikiGenerationManagementProps> = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Wiki生成管理</CardTitle>
        <CardDescription>管理和配置Wiki文档生成</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground">Wiki生成管理功能开发中...</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default WikiGenerationManagement
