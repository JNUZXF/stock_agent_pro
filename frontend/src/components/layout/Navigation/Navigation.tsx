/**
 * 导航栏组件 - AETHER UI 风格
 * 提供页面导航功能
 */

import { Link, useLocation } from 'react-router-dom';
import { Home, MessageSquare, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../../lib/cn';
import { typographyStyles } from '../../../styles/typography';

export interface NavigationProps {
  /**
   * 是否为深度思考模式
   */
  isDeepThinking?: boolean;
  /**
   * 自定义类名
   */
  className?: string;
}

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { path: '/', label: '主页', icon: <Home size={18} /> },
  { path: '/chat', label: '对话', icon: <MessageSquare size={18} /> },
  // 可以后续添加更多导航项
  // { path: '/settings', label: '设置', icon: <Settings size={18} /> },
];

export const Navigation = ({ isDeepThinking = false, className }: NavigationProps) => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav
      className={cn(
        'backdrop-blur-xl bg-black/40 border-b border-white/10',
        className
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo/品牌 */}
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className={cn(
                'flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-300',
                'hover:bg-white/10',
                isDeepThinking ? 'hover:bg-yellow-500/10' : 'hover:bg-cyan-500/10'
              )}
            >
              <div
                className={cn(
                  'p-1.5 rounded-md transition-all duration-500',
                  isDeepThinking
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-cyan-500/20 text-cyan-400'
                )}
              >
                <MessageSquare size={18} />
              </div>
              <span className="font-bold text-lg tracking-wide">
                Stock <span className={cn('font-thin', typographyStyles.textSecondary)}>Agent</span>
              </span>
            </Link>
          </div>

          {/* 桌面端导航菜单 */}
          <div className="hidden md:flex items-center gap-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300',
                    'hover:bg-white/10',
                    isActive
                      ? isDeepThinking
                        ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                        : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-white hover:text-white border border-transparent'
                  )}
                >
                  {item.icon}
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* 移动端菜单按钮 */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className={cn(
              'md:hidden p-2 rounded-lg transition-all duration-300',
              'hover:bg-white/10',
              isMobileMenuOpen
                ? isDeepThinking
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-cyan-500/20 text-cyan-400'
                : 'text-white'
            )}
            aria-label="切换菜单"
          >
            {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* 移动端下拉菜单 */}
        {isMobileMenuOpen && (
          <div className="md:hidden pb-4 border-t border-white/10 mt-2 pt-4">
            <div className="flex flex-col gap-2">
              {navItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={cn(
                      'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300',
                      isActive
                        ? isDeepThinking
                          ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                          : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-white hover:bg-white/10 hover:text-white'
                    )}
                  >
                    {item.icon}
                    <span className="text-sm font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};
