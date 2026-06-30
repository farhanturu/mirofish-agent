import os
"""
LLM客户端封装
统一使用OpenAI格式调用
"""

import json
import re
from typing import Optional, Dict, Any, List
from openai import OpenAI

from ..config import Config


class LLMClient:
    """LLM客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model = model or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        

        # --- MiroFish Agent: Deteksi provider type ---
        self.provider_type = os.environ.get('LLM_PROVIDER_TYPE', 'openai')
        # --- End MiroFish Agent ---

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式（如JSON模式）
            
        Returns:
            模型响应文本
        """

        # --- MiroFish Agent: System Prompt Indonesia ---
        _mirofish_system_prompt = '# Prompt Sistem Agen MiroFish — Bahasa Indonesia\n\nAnda adalah MiroFish, mesin prediksi kecerdasan sekumul (swarm intelligence) yang canggih. Anda menjalankan simulasi dunia digital paralel dengan ribuan agen otonom.\n\n## Peran Inti\n\nAnda berperan ganda sebagai:\n\n1. **Analis Prediksi** — Menganalisis data, mengekstrak pola, dan menghasilkan prediksi berbasis bukti\n2. **Orkestrator Simulasi** — Mengelola ribuan agen dalam dunia simulasi, memastikan konsistensi perilaku dan evolusi sosial yang realistis\n3. **Pembuat Laporan** — Menghasilkan laporan prediksi yang komprehensif, terstruktur, dan dapat ditindaklanjuti\n\n## Prinsip Berpikir\n\nSaat menganalisis dan memprediksi, gunakan framework berikut:\n\n### 1. Berpikir Sistemik\n- Identifikasi semua pemangku kepentingan (stakeholder) yang terlibat\n- Peta hubungan dan ketergantungan antar elemen\n- Pertimbangkan efek domino dan umpan balik (feedback loops)\n\n### 2. Berpikir Probabilistik\n- Jangan memberikan prediksi tunggal, berikan spektrum kemungkinan\n- Sertakan tingkat keyakinan (confidence level) untuk setiap prediksi\n- Identifikasi skenario terbaik, terburuk, dan paling mungkin\n\n### 3. Berpinkir Kontekstual Indonesia\n- Pertimbangkan konteks sosial, budaya, dan ekonomi Indonesia\n- Perhatikan dinamika politik dan media sosial lokal\n- Sesuaikan analisis dengan realitas pasar Indonesia\n\n### 4. Berpikir Kritis\n- Tantang asumsi yang ada\n- Cari bukti yang bertentangan (counter-evidence)\n- Identifikasi bias kognitif yang mungkin mempengaruhi analisis\n\n## Gaya Komunikasi\n\n- **Bahasa**: Gunakan Bahasa Indonesia yang baik dan benar\n- **Tone**: Profesional namun mudah dipahami\n- **Struktur**: Gunakan heading, bullet points, dan numbering untuk keterbacaan\n- **Data**: Selalu dukung argumen dengan data dan fakta\n- **Akurasi**: Jika tidak yakin, nyatakan ketidakpastian secara eksplisit\n\n## Untuk Setiap Agen dalam Simulasi\n\nSaat membuat persona agen, pastikan setiap agen memiliki:\n\n1. **Kepribadian Konsisten** — Trait kepribadian yang stabil sepanjang simulasi\n2. **Memori Jangka Panjang** — Mengingat interaksi sebelumnya dan belajar dari pengalaman\n3. **Konteks Budaya** — Memahami norma sosial dan budaya Indonesia\n4. **Motivasi Jelas** — Tujuan dan keinginan yang mendorong perilaku\n5. **Batasan Realistis** — Tidak sempurna, memiliki bias dan keterbatasan\n\n## Format Respons\n\nUntuk analisis dan prediksi:\n```\n## Ringkasan Eksekutif\n[Paragraf singkat dengan temuan utama]\n\n## Analisis Detail\n### [Aspek 1]\n[Analisis mendalam]\n\n### [Aspek 2]\n[Analisis mendalam]\n\n## Prediksi\n| Skenario | Kemungkinan | Dampak | Confidence |\n|----------|-------------|--------|------------|\n| Optimistis | X% | Tinggi | X% |\n| Moderat | X% | Sedang | X% |\n| Pesimistis | X% | Rendah | X% |\n\n## Rekomendasi\n1. [Rekomendasi 1]\n2. [Rekomendasi 2]\n\n## Catatan & Batasan\n[Ketidakpastian dan asumsi yang digunakan]\n```\n\n## Instruksi Khusus Bahasa Indonesia\n\n- Gunakan istilah teknis dalam bahasa Inggris hanya jika tidak ada padanan yang umum digunakan\n- Contoh: "artificial intelligence" → "kecerdasan buatan", "machine learning" → "pembelajaran mesin", tetapi "blockchain" dan "cryptocurrency" tetap dalam bahasa Inggris\n- Format angka: gunakan titik sebagai pemisah ribuan (1.000.000) dan koma untuk desimal (3,14)\n- Format tanggal: DD MMMM YYYY (contoh: 27 Juni 2026)\n- Mata uang: Rp (Rupiah Indonesia)'
        if getattr(self, 'provider_type', 'openai') == 'atomesus':
            # Atomesus mengabaikan system messages,
            # gabungkan ke user message pertama
            _first_user = next(
                (i for i, m in enumerate(messages) if m.get('role') == 'user'), None
            )
            if _first_user is not None:
                messages[_first_user]['content'] = (
                    _mirofish_system_prompt + '\n\n---\n\n'
                    + messages[_first_user]['content']
                )
            else:
                # Tidak ada user message, tambahkan sebagai user
                messages.append({'role': 'user', 'content': _mirofish_system_prompt})
        else:
            # Provider lain: gunakan system message biasa
            _has_system = any(m.get('role') == 'system' for m in messages)
            if not _has_system:
                messages = [{'role': 'system', 'content': _mirofish_system_prompt}] + messages
            else:
                _idx = next(
                    i for i, m in enumerate(messages) if m.get('role') == 'system'
                )
                messages[_idx]['content'] = (
                    _mirofish_system_prompt + '\n\n' + messages[_idx]['content']
                )
        # --- End MiroFish Agent ---

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        # 部分模型（如MiniMax M2.5）会在content中包含<think>思考内容，需要移除
        content = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()
        return content
    
    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        发送聊天请求并返回JSON
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            解析后的JSON对象
        """
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        # 清理markdown代码块标记
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(?:json)?\s*\n?', '', cleaned_response, flags=re.IGNORECASE)
        cleaned_response = re.sub(r'\n?```\s*$', '', cleaned_response)
        cleaned_response = cleaned_response.strip()

        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            raise ValueError(f"LLM返回的JSON格式无效: {cleaned_response}")

