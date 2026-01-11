import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Brain, Zap, Shield, BarChart3, MessageSquare, ChevronDown } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useEffect, useRef, useState } from 'react';

// 神经网络背景组件
const NeuralNetwork = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const nodes: { x: number; y: number; vx: number; vy: number }[] = [];
    const nodeCount = 50;

    // 创建节点
    for (let i = 0; i < nodeCount; i++) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
      });
    }

    let animationId: number;

    const animate = () => {
      ctx.fillStyle = 'rgba(15, 23, 42, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 更新和绘制节点
      nodes.forEach((node, i) => {
        node.x += node.vx;
        node.y += node.vy;

        // 边界检测
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

        // 绘制节点
        ctx.beginPath();
        ctx.arc(node.x, node.y, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(99, 102, 241, 0.5)';
        ctx.fill();

        // 连接附近的节点
        nodes.slice(i + 1).forEach((otherNode) => {
          const dx = node.x - otherNode.x;
          const dy = node.y - otherNode.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 150) {
            ctx.beginPath();
            ctx.moveTo(node.x, node.y);
            ctx.lineTo(otherNode.x, otherNode.y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${0.2 * (1 - distance / 150)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        });
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none" />;
};

// 浮动粒子组件
const FloatingParticles = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-full"
          animate={{
            x: [Math.random() * window.innerWidth, Math.random() * window.innerWidth],
            y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight],
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: "linear",
          }}
          style={{
            left: Math.random() * 100 + '%',
            top: Math.random() * 100 + '%',
          }}
        />
      ))}
    </div>
  );
};

// 3D 卡片组件
interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  gradient: string;
  delay: number;
}

const FeatureCard = ({ icon, title, description, gradient, delay }: FeatureCardProps) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      viewport={{ once: true }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="group relative"
    >
      <motion.div
        className={`relative p-8 rounded-2xl bg-gradient-to-br ${gradient} backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden`}
        whileHover={{ y: -10, scale: 1.02 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
      >
        {/* 光晕效果 */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent opacity-0 group-hover:opacity-100"
          transition={{ duration: 0.3 }}
        />

        {/* 图标 */}
        <motion.div
          className="relative z-10 w-16 h-16 mb-6 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center"
          animate={isHovered ? { rotate: 360, scale: 1.1 } : { rotate: 0, scale: 1 }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-white">{icon}</div>
        </motion.div>

        {/* 内容 */}
        <h3 className="relative z-10 text-2xl font-bold text-white mb-3">{title}</h3>
        <p className="relative z-10 text-white/80 leading-relaxed">{description}</p>

        {/* 装饰性元素 */}
        <motion.div
          className="absolute -right-4 -bottom-4 w-24 h-24 bg-white/5 rounded-full blur-2xl"
          animate={{ scale: isHovered ? 1.5 : 1 }}
          transition={{ duration: 0.3 }}
        />
      </motion.div>
    </motion.div>
  );
};

export default function LandingPage() {
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-purple-900 text-white overflow-hidden">
      {/* 背景效果 */}
      <NeuralNetwork />
      <FloatingParticles />

      {/* Hero Section */}
      <motion.section
        style={{ opacity, scale }}
        className="relative min-h-screen flex items-center justify-center px-6"
      >
        <div className="max-w-6xl mx-auto text-center relative z-10">
          {/* Logo/Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="inline-flex items-center gap-2 px-6 py-3 mb-8 rounded-full bg-white/10 backdrop-blur-md border border-white/20"
          >
            <Sparkles className="w-5 h-5 text-yellow-300" />
            <span className="text-sm font-medium">AI 驱动的智能股票分析</span>
          </motion.div>

          {/* 主标题 */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-6xl md:text-8xl font-black mb-6 leading-tight"
          >
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 animate-gradient">
              Stock Agent Pro
            </span>
          </motion.h1>

          {/* 副标题 */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl md:text-2xl text-white/80 mb-12 max-w-3xl mx-auto leading-relaxed"
          >
            让 AI 成为你的专属投资顾问，实时分析市场动态，
            <br />
            <span className="text-blue-300 font-semibold">精准把握每一次投资机会</span>
          </motion.p>

          {/* CTA 按钮 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
          >
            <Link to="/chat">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(99, 102, 241, 0.5)" }}
                whileTap={{ scale: 0.95 }}
                className="group px-10 py-5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full text-lg font-bold shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 flex items-center gap-3"
              >
                开始对话
                <motion.div
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-5 h-5" />
                </motion.div>
              </motion.button>
            </Link>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-10 py-5 bg-white/10 backdrop-blur-md rounded-full text-lg font-semibold border border-white/20 hover:bg-white/20 transition-all duration-300"
            >
              了解更多
            </motion.button>
          </motion.div>

          {/* 滚动提示 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <ChevronDown className="w-8 h-8 text-white/50" />
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* 特性展示区 */}
      <section className="relative py-32 px-6">
        <div className="max-w-7xl mx-auto">
          {/* 标题 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-20"
          >
            <h2 className="text-5xl font-black mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              为什么选择我们？
            </h2>
            <p className="text-xl text-white/70 max-w-2xl mx-auto">
              结合最先进的 AI 技术与专业的金融分析能力
            </p>
          </motion.div>

          {/* 特性卡片网格 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Brain className="w-8 h-8" />}
              title="智能分析"
              description="基于深度学习的 AI 模型，实时分析海量市场数据，为你提供精准的投资建议"
              gradient="from-indigo-600/40 to-blue-600/40"
              delay={0.1}
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8" />}
              title="实时响应"
              description="毫秒级的数据处理速度，让你在瞬息万变的市场中抢占先机"
              gradient="from-purple-600/40 to-pink-600/40"
              delay={0.2}
            />
            <FeatureCard
              icon={<Shield className="w-8 h-8" />}
              title="安全可靠"
              description="银行级的数据加密和隐私保护，确保你的投资信息绝对安全"
              gradient="from-blue-600/40 to-cyan-600/40"
              delay={0.3}
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="数据可视化"
              description="直观的图表展示，让复杂的市场数据一目了然，辅助你做出明智决策"
              gradient="from-green-600/40 to-emerald-600/40"
              delay={0.4}
            />
            <FeatureCard
              icon={<MessageSquare className="w-8 h-8" />}
              title="自然对话"
              description="像和朋友聊天一样轻松，用自然语言提问，AI 会给你专业的解答"
              gradient="from-pink-600/40 to-rose-600/40"
              delay={0.5}
            />
            <FeatureCard
              icon={<TrendingUp className="w-8 h-8" />}
              title="趋势预测"
              description="利用机器学习算法，预测市场走势，帮你提前布局未来投资"
              gradient="from-orange-600/40 to-red-600/40"
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* Demo 预览区 */}
      <section className="relative py-32 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="relative"
          >
            {/* 装饰性背景 */}
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-3xl blur-3xl" />

            {/* Demo 容器 */}
            <div className="relative bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 p-8 shadow-2xl">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>

              {/* 模拟对话 */}
              <div className="space-y-4">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  viewport={{ once: true }}
                  className="flex gap-3"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-sm font-bold">
                    You
                  </div>
                  <div className="flex-1 bg-blue-500/20 backdrop-blur-md rounded-2xl rounded-tl-sm px-6 py-4 border border-blue-500/30">
                    <p className="text-white/90">帮我分析一下特斯拉最近的股价走势</p>
                  </div>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  viewport={{ once: true }}
                  className="flex gap-3"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  <div className="flex-1 bg-white/10 backdrop-blur-md rounded-2xl rounded-tl-sm px-6 py-4 border border-white/10">
                    <p className="text-white/90 leading-relaxed">
                      根据最新的市场数据分析，特斯拉（TSLA）在过去一周呈现上升趋势...
                      <br />
                      <span className="text-green-400 font-semibold mt-2 inline-block">
                        📈 建议关注 $245-$250 区间的支撑位
                      </span>
                    </p>
                  </div>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA 区域 */}
      <section className="relative py-32 px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto text-center"
        >
          <h2 className="text-5xl font-black mb-6">
            准备好开始你的
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              {' '}智能投资之旅{' '}
            </span>
            了吗？
          </h2>
          <p className="text-xl text-white/70 mb-12">
            现在就和 AI 投资顾问开始对话，发现更多投资机会
          </p>
          <Link to="/chat">
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 0 40px rgba(99, 102, 241, 0.6)" }}
              whileTap={{ scale: 0.95 }}
              className="px-12 py-6 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-full text-xl font-bold shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 inline-flex items-center gap-3"
            >
              立即开始
              <ArrowRight className="w-6 h-6" />
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 border-t border-white/10">
        <div className="max-w-6xl mx-auto text-center text-white/50">
          <p>© 2026 Stock Agent Pro. Powered by Advanced AI Technology.</p>
        </div>
      </footer>

      {/* CSS 动画 */}
      <style>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
      `}</style>
    </div>
  );
}
