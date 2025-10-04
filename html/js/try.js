// 留言板功能
const commentForm = document.getElementById('commentForm');
const commentsList = document.getElementById('commentsList');

// 从 localStorage 加载留言
function loadComments() {
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    commentsList.innerHTML = '';
    
    comments.forEach(comment => {
        const commentElement = document.createElement('div');
        commentElement.className = 'comment-item';
        commentElement.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${comment.name}</span>
                <span class="comment-time">${comment.time}</span>
            </div>
            <div class="comment-content">${comment.message}</div>
        `;
        commentsList.appendChild(commentElement);
    });
}

// 提交留言
commentForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    
    const comment = {
        name: name,
        email: email,
        message: message,
        time: new Date().toLocaleString('zh-CN')
    };
    
    // 保存到 localStorage
    const comments = JSON.parse(localStorage.getItem('comments')) || [];
    comments.unshift(comment);
    localStorage.setItem('comments', JSON.stringify(comments));
    
    // 清空表单
    commentForm.reset();
    
    // 重新加载留言
    loadComments();
    
    // 同时发送弹幕
    sendDanmaku(message, name);
});

// 弹幕功能
const canvas = document.getElementById('danmakuCanvas');
const ctx = canvas.getContext('2d');
let danmakus = [];

// 初始化画布
function initCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

// 弹幕类
class Danmaku {
    constructor(text, color = '#fff') {
        this.text = text;
        this.color = color;
        this.x = canvas.width;
        this.y = Math.random() * (canvas.height - 50) + 25;
        this.speed = 2 + Math.random() * 2;
        this.opacity = 1;
        this.fontSize = 18 + Math.random() * 10;
    }
    
    update() {
        this.x -= this.speed;
        return this.x > -200;
    }
    
    draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.font = `bold ${this.fontSize}px Arial`;
        ctx.fillStyle = this.color;
        ctx.fillText(this.text, this.x, this.y);
        
        // 添加文字阴影
        ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
        ctx.shadowBlur = 10;
        ctx.shadowOffsetX = 2;
        ctx.shadowOffsetY = 2;
        ctx.restore();
    }
}

// 发送弹幕
function sendDanmaku(text = null, author = null) {
    const input = document.getElementById('danmakuInput');
    const danmakuText = text || input.value;
    
    if (danmakuText.trim()) {
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        let displayText = danmakuText;
        if (author && !text) {
            displayText = `${author}: ${danmakuText}`;
        }
        
        danmakus.push(new Danmaku(displayText, color));
        
        if (!text) {
            input.value = '';
        }
    }
}

// 动画循环
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 更新和绘制所有弹幕
    danmakus = danmakus.filter(danmaku => danmaku.update());
    danmakus.forEach(danmaku => danmaku.draw());
    
    requestAnimationFrame(animate);
}

// 初始化
window.addEventListener('load', function() {
    initCanvas();
    loadComments();
    animate();
    
    // 添加一些示例弹幕
    setTimeout(() => {
        sendDanmaku('欢迎来到留言板！');
        sendDanmaku('这个页面真不错~');
        sendDanmaku('大家快来留言呀！');
        sendDanmaku('弹幕效果很酷！');
        sendDanmaku('支持实时互动！');
    }, 1000);
});

window.addEventListener('resize', initCanvas);

// 回车发送弹幕
document.getElementById('danmakuInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendDanmaku();
    }
});

// 添加随机弹幕生成（可选）
setInterval(() => {
    const randomMessages = [
        '这个留言板很棒！',
        '弹幕效果很流畅',
        '界面设计很漂亮',
        '功能很实用',
        '支持实时互动',
        '用户体验很好'
    ];
    const randomMessage = randomMessages[Math.floor(Math.random() * randomMessages.length)];
    sendDanmaku(randomMessage);
}, 10000); // 每10秒发送一条随机弹幕