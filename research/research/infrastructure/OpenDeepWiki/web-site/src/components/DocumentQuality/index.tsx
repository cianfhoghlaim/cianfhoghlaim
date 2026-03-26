// 文档质量评估组件

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity } from 'lucide-react'

interface DocumentQualityEvaluationProps {
  warehouseId: string
}

export const DocumentQualityEvaluation: React.FC<DocumentQualityEvaluationProps> = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>文档质量评估</CardTitle>
        <CardDescription>评估和分析文档质量</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-muted-foreground">文档质量评估功能开发中...</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default DocumentQualityEvaluation
