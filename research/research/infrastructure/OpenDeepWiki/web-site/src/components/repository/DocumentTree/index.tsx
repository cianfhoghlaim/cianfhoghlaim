// 文档树组件

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import {
  ChevronRight,
  FileText,
  Folder,
  FolderOpen
} from 'lucide-react'

export interface DocumentNode {
  id: string
  name: string
  type: 'file' | 'folder'
  path: string
  children?: DocumentNode[]
  isExpanded?: boolean
  level?: number
  description?: string
  lastUpdate?: string
  disabled?: boolean  // 是否禁用（正在生成中）
  progress?: number   // 生成进度 (0-100)
}

interface DocumentTreeProps {
  nodes: DocumentNode[]
  selectedPath?: string
  onSelectNode?: (node: DocumentNode) => void
  className?: string
}

const TreeNode: React.FC<{
  node: DocumentNode
  level: number
  selectedPath?: string
  onSelectNode?: (node: DocumentNode) => void
  onToggleExpand?: (node: DocumentNode) => void
}> = ({ node, level, selectedPath, onSelectNode, onToggleExpand }) => {
  const [isExpanded, setIsExpanded] = useState(node.isExpanded || false)

  const handleToggle = () => {
    setIsExpanded(!isExpanded)
    if (onToggleExpand) {
      onToggleExpand({ ...node, isExpanded: !isExpanded })
    }
  }

  const handleSelect = () => {
    if (node.type === 'file' && onSelectNode) {
      onSelectNode(node)
    } else if (node.type === 'folder') {
      handleToggle()
    }
  }

  const isSelected = selectedPath === node.path

  return (
    <div className="animate-in fade-in-0 slide-in-from-left-1 duration-200">
      <div
        className={cn(
          "flex items-center gap-1 px-2 py-1.5 rounded-md cursor-pointer",
          "transition-all duration-200 ease-in-out",
          "hover:bg-accent hover:text-accent-foreground hover:translate-x-0.5",
          isSelected && "bg-accent text-accent-foreground font-medium shadow-sm",
          level > 0 && "ml-4"
        )}
        onClick={handleSelect}
      >
        {node.type === 'folder' && (
          <button
            className="p-0.5 hover:bg-accent/50 rounded transition-transform duration-200"
            onClick={(e) => {
              e.stopPropagation()
              handleToggle()
            }}
          >
            <ChevronRight
              className={cn(
                "h-3 w-3 transition-transform duration-200",
                isExpanded && "rotate-90"
              )}
            />
          </button>
        )}

        {node.type === 'folder' ? (
          isExpanded ? (
            <FolderOpen className="h-4 w-4 text-blue-500" />
          ) : (
            <Folder className="h-4 w-4 text-blue-500" />
          )
        ) : (
          <FileText className="h-4 w-4 text-gray-500 ml-5" />
        )}

        <span className="text-sm truncate flex-1">{node.name}</span>
      </div>

      {node.type === 'folder' && node.children && node.children.length > 0 && (
        <div
          className={cn(
            "overflow-hidden transition-all duration-300 ease-in-out",
            isExpanded ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
          )}
        >
          {node.children.filter(child => child != null).map((child) => (
            <TreeNode
              key={child.id || child.path}
              node={child}
              level={level + 1}
              selectedPath={selectedPath}
              onSelectNode={onSelectNode}
              onToggleExpand={onToggleExpand}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export const DocumentTree: React.FC<DocumentTreeProps> = ({
  nodes,
  selectedPath,
  onSelectNode,
  className
}) => {
  // Filter out any undefined or null nodes
  const validNodes = nodes?.filter(node => node != null) || []

  return (
    <div className={cn("space-y-0.5", className)}>
      {validNodes.map((node) => (
        <TreeNode
          key={node.id || node.path}
          node={node}
          level={0}
          selectedPath={selectedPath}
          onSelectNode={onSelectNode}
        />
      ))}
    </div>
  )
}

export default DocumentTree