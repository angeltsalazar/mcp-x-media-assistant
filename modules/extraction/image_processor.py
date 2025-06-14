"""
Módulo para procesar URLs de status y convertirlas en URLs de imágenes directas.
"""
import asyncio
import random
from playwright.async_api import Page
from ..utils.logging import Logger
from ..utils.url_utils import URLUtils
from ..utils.cache_manager import CacheManager

class ImageProcessor:
    """
    Contiene la lógica para transformar las URLs de los tweets en URLs
    de imágenes directas y de alta calidad, con cache para optimizar rendimiento.
    """
    def __init__(self, page: Page):
        self.page = page
        self.processed_image_urls: set[str] = set()
        self.username = None
        self.cache_manager = None

    async def convert_status_to_image_urls(self, status_urls: list[dict], username: str = None, url_limit: int = None) -> tuple[list[str], dict]:
        """
        Orquesta la conversión de URLs de status a URLs de imágenes directas
        utilizando múltiples métodos para maximizar los resultados.
        Usa cache para evitar reprocesamiento innecesario.
        
        Args:
            status_urls: Lista de URLs de status a procesar
            username: Username para el cache
            url_limit: Límite de URLs nuevas (no cacheadas) a procesar
            
        Returns:
            tuple: (image_urls, url_to_status_mapping)
        """
        # Actualizar username si se proporciona
        if username:
            self.username = username
            self.cache_manager = CacheManager()
        
        Logger.info("🔄 Iniciando conversión de URLs de status a imágenes directas...")
        
        image_status_urls = [item for item in status_urls if item.get('media_type') == 'image']
        
        # Contar videos para calcular el límite correcto de imágenes
        videos = [item for item in status_urls if item.get('media_type') == 'video']
        total_status = len(status_urls)
        video_count = len(videos)
        expected_images = total_status - video_count  # Límite dinámico basado en status reales
        
        Logger.info(f"📊 Se procesarán {len(image_status_urls)} URLs de status de tipo imagen.")
        Logger.info(f"📊 Status totales: {total_status}, Videos: {video_count}, Imágenes esperadas: {expected_images}")

        image_urls = []
        new_mappings = {}  # Para actualizar el cache: status_id -> [image_urls]
        
        # Usar cache si está disponible
        if self.cache_manager and self.username:
            cached_urls, uncached_status_urls = self.cache_manager.get_cached_image_urls(
                self.username, image_status_urls
            )
            image_urls.extend(cached_urls)
            image_status_urls = uncached_status_urls
            Logger.info(f"💾 {len(cached_urls)} imágenes obtenidas del cache")
        
        # Aplicar límite a URLs nuevas (no cacheadas) si se especifica
        original_uncached_count = len(image_status_urls)
        if url_limit is not None and len(image_status_urls) > url_limit:
            image_status_urls = image_status_urls[:url_limit]
            Logger.info(f"⚡ Límite aplicado: procesando {len(image_status_urls)} de {original_uncached_count} URLs nuevas")
        
        # Extraer username para filtrar correctamente
        target_username = None
        if image_status_urls:
            first_url = image_status_urls[0].get('url', '')
            url_parts = first_url.split('/')
            if len(url_parts) > 3:
                target_username = url_parts[3]  # x.com/username/status/id
        
        Logger.info(f"🎯 Procesando imágenes del usuario: @{target_username}")
        
        # Procesar solo las URLs no cacheadas (respetando el límite)
        if image_status_urls:
            Logger.info(f"🔄 Procesando {len(image_status_urls)} URLs nuevas...")
            
            # MÉTODO 1: Extracción desde el DOM (rápido y eficiente)
            dom_converted, dom_mappings = await self._extract_from_dom(image_urls, expected_images, image_status_urls, target_username)
            new_mappings.update(dom_mappings)
            
            # MÉTODO 2: Construcción directa navegando a cada status (más preciso)
            # Solo procesar las URLs que no se pudieron mapear en el método 1
            remaining_unmapped = [url for url in image_status_urls if self._extract_status_id(url.get('url', '')) not in new_mappings]
            
            if remaining_unmapped:
                constructed_count, method2_mappings = await self._construct_direct_urls_improved(
                    remaining_unmapped, image_urls, expected_images, target_username
                )
                new_mappings.update(method2_mappings)
            else:
                constructed_count = 0
            
            # MÉTODO 3: Fallback con extracción alternativa si es necesario
            if len(image_urls) < expected_images:
                await self._fallback_image_extraction(image_status_urls, image_urls, expected_images)
            
            # Actualizar cache con nuevos mapeos válidos 
            if self.cache_manager and self.username and new_mappings:
                # Convertir mapeos múltiples a formato de cache (solo primera imagen por status)
                valid_mappings = {}
                for status_id, images in new_mappings.items():
                    if isinstance(images, list) and images:
                        valid_mappings[status_id] = images[0]  # Solo la primera imagen
                    elif isinstance(images, str) and images:
                        valid_mappings[status_id] = images
                
                if valid_mappings:
                    self.cache_manager.update_cache_with_new_mappings(self.username, valid_mappings)
                Logger.info(f"💾 Cache actualizado con {len(valid_mappings)} nuevos mapeos válidos")
        else:
            dom_converted = 0
            constructed_count = 0

        total_converted = len(image_urls)
        total_mappings = sum(len(v) if isinstance(v, list) else 1 for v in new_mappings.values())
        conversion_rate = (total_converted / expected_images * 100) if expected_images else 0
        
        Logger.success(f"🎯 RESUMEN FINAL:")
        Logger.info(f"   💾 Cache: {len(image_urls) - dom_converted - constructed_count} imágenes")
        Logger.info(f"   🔍 Método 1 (DOM): {dom_converted} imágenes")
        Logger.info(f"   🔧 Método 2 (Construcción directa): {constructed_count} imágenes")
        Logger.info(f"   📊 Total convertidas: {total_converted}/{expected_images} ({conversion_rate:.1f}%)")
        Logger.info(f"   🗂️  Mapeos para cache: {total_mappings} imágenes mapeadas")
        
        # Mostrar información sobre límite aplicado si corresponde
        if url_limit is not None and original_uncached_count > url_limit:
            Logger.info(f"   ⚡ Límite aplicado: {url_limit} de {original_uncached_count} URLs nuevas procesadas")
            Logger.info(f"   📝 Quedaron {original_uncached_count - url_limit} URLs nuevas por procesar")
        
        # Crear mapeo completo de URLs a status_ids - MEJORADO
        complete_mapping = {}
        
        # Agregar mapeos desde cache
        if self.cache_manager and self.username:
            cache_mapping = self.cache_manager.get_url_to_status_mapping(self.username, image_urls)
            complete_mapping.update(cache_mapping)
        
        # Agregar mapeos nuevos - Manejar múltiples imágenes por status
        for status_id, images in new_mappings.items():
            if isinstance(images, list):
                for image_url in images:
                    if image_url and image_url in image_urls:
                        complete_mapping[image_url] = status_id
            elif isinstance(images, str) and images in image_urls:
                complete_mapping[images] = status_id
        
        # NO crear mapeos adicionales por correlación - esto causaba el problema
        # Solo usar mapeos explícitos y confiables
        unmapped_count = len([url for url in image_urls if url not in complete_mapping])
        if unmapped_count > 0:
            Logger.warning(f"   ⚠️  {unmapped_count} imágenes quedarán sin status_id específico")
            Logger.info(f"   💡 Esto es normal para imágenes en carruseles múltiples")
        
        return image_urls, complete_mapping

    async def _extract_from_dom(self, image_urls: list[str], expected_images: int, status_urls: list[dict], target_username: str = None) -> tuple[int, dict]:
        """
        MÉTODO 1: Extrae las URLs de las imágenes directamente desde los elementos <img>
        cargados en la página y trata de correlacionarlas con status URLs.
        Returns: (dom_converted_count, status_id_to_image_mappings)
        """
        Logger.info("🔍 MÉTODO 1: Extrayendo imágenes desde el DOM...")
        
        # Extraer username del primer status URL para filtrar correctamente si no se proporciona
        if not target_username and status_urls:
            first_url = status_urls[0].get('url', '')
            url_parts = first_url.split('/')
            if len(url_parts) > 3:
                target_username = url_parts[3]  # x.com/username/status/id
        
        Logger.info(f"🎯 Filtrando imágenes solo del usuario: @{target_username}")
        
        all_page_images = await self.page.evaluate("""
            (targetUsername) => {
                const images = [];
                const imgElements = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                imgElements.forEach(img => {
                    if (img.src && img.src.includes('pbs.twimg.com') && 
                        !img.src.includes('profile_images') && 
                        !img.src.includes('profile_banners')) {
                        
                        // Obtener el contenedor del tweet para verificar el usuario
                        const tweetContainer = img.closest('article') || img.closest('[data-testid="tweet"]');
                        let belongsToTargetUser = false;
                        
                        if (tweetContainer && targetUsername) {
                            // Buscar enlaces de usuario en el tweet
                            const userLinks = tweetContainer.querySelectorAll('a[href*="/' + targetUsername + '"]');
                            belongsToTargetUser = Array.from(userLinks).some(link => {
                                const href = link.getAttribute('href');
                                return href && href.includes('/' + targetUsername) && !href.includes('/status/');
                            });
                        }
                        
                        images.push({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || img.width || 0,
                            height: img.naturalHeight || img.height || 0,
                            belongsToTargetUser: belongsToTargetUser,
                            hasContainer: !!tweetContainer
                        });
                    }
                });
                return images;
            }
        """, target_username)
        
        Logger.info(f"   📊 Encontradas {len(all_page_images)} imágenes totales en la página")
        
        # Filtrar imágenes que pertenecen al usuario objetivo y parecen ser de tweets
        tweet_images = []
        user_images = [img for img in all_page_images if img.get('belongsToTargetUser', False)]
        Logger.info(f"   🎯 Filtradas {len(user_images)} imágenes del usuario @{target_username}")
        
        for img_data in user_images:
            # Filtrar por tamaño (evitar avatares pequeños) y verificar que sea del usuario correcto
            if img_data['width'] > 100 and img_data['height'] > 100:
                tweet_images.append(img_data)
            elif img_data['hasContainer']:  # O si está en un contenedor de tweet
                tweet_images.append(img_data)
        
        Logger.info(f"   🎯 Filtradas {len(tweet_images)} imágenes que parecen ser de tweets")
        
        # Añadir imágenes limpias y crear mapeos
        dom_converted = 0
        dom_mappings = {}
        
        for i, img_data in enumerate(tweet_images):
            clean_img_url = URLUtils.clean_image_url_robust(img_data['src'])
            if clean_img_url and clean_img_url not in image_urls:
                # Filtrar thumbnails de video que no son imágenes reales
                if 'amplify_video_thumb' not in clean_img_url and 'video_thumb' not in clean_img_url:
                    image_urls.append(clean_img_url)
                    dom_converted += 1
                    
                    # Tratar de correlacionar con status URL usando el índice o el parent_href
                    if i < len(status_urls):
                        status_id = self._extract_status_id(status_urls[i].get('url', ''))
                        if status_id:
                            dom_mappings[status_id] = clean_img_url
                            Logger.info(f"   ✅ [{i+1}] Imagen DOM mapeada: {status_id} -> {clean_img_url}")
                        else:
                            Logger.info(f"   ✅ [{i+1}] Imagen DOM añadida: {clean_img_url}")
                    else:
                        Logger.info(f"   ✅ [{i+1}] Imagen DOM añadida: {clean_img_url}")
                else:
                    Logger.warning(f"   🎬 Thumbnail de video excluido: {clean_img_url}")
                
                # No limitar artificialmente - permitir múltiples imágenes por tweet
                # if len(image_urls) >= expected_images:
                #     Logger.warning(f"   🛑 Límite de {expected_images} imágenes alcanzado")
                #     break
        
        Logger.info(f"   ✅ Método 1 completado: {dom_converted} imágenes añadidas, {len(dom_mappings)} mapeos creados")
        return dom_converted, dom_mappings

    async def _construct_direct_urls_improved(self, image_status_urls: list[dict], image_urls: list[str], expected_images: int, target_username: str = None) -> tuple[int, dict]:
        """
        MÉTODO 2 MEJORADO: Navegar directamente a cada URL de status para extraer TODAS las imágenes
        Maneja correctamente carruseles con múltiples imágenes por tweet
        Returns: (constructed_count, status_to_image_mappings)
        """
        Logger.info(f"   🔧 MÉTODO 2 MEJORADO: Construyendo URLs directas navegando a {len(image_status_urls)} status...")
        
        constructed_count = 0
        status_mappings = {}  # status_id -> [list_of_image_urls] or single_image_url
        # Usar todas las URLs disponibles - el límite ya se aplicó anteriormente
        remaining_status_urls = image_status_urls  # Procesar todas las URLs que pasaron el filtro de límite
        
        for i, item in enumerate(remaining_status_urls, 1):
            try:
                status_url = item.get('url')
                if not status_url:
                    continue
                
                status_id = self._extract_status_id(status_url)
                if not status_id:
                    continue
                
                Logger.info(f"   🔍 [{i}/{len(remaining_status_urls)}] Navegando a: {status_url}")
                
                try:
                    await self.page.goto(status_url, wait_until="domcontentloaded", timeout=15000)
                    # Espera orgánica después de la navegación para simular tiempo de lectura
                    page_load_delay = random.uniform(1.5, 3.0)
                    await asyncio.sleep(page_load_delay)
                    
                    # Buscar imágenes SOLO del tweet principal, no de los replies
                    tweet_images = await self.page.evaluate("""
                        (statusUrl) => {
                            const images = [];
                            
                            // Extraer el username del status URL
                            const urlParts = statusUrl.split('/');
                            const expectedUsername = urlParts[3]; // x.com/username/status/id
                            
                            // Buscar específicamente el tweet principal (no replies)
                            const tweetContainers = document.querySelectorAll('article, [data-testid="tweet"]');
                            
                            for (const container of tweetContainers) {
                                // Verificar que este tweet pertenece al usuario correcto
                                const userLinks = container.querySelectorAll('a[href*="/' + expectedUsername + '"]');
                                const isMainUser = Array.from(userLinks).some(link => {
                                    const href = link.getAttribute('href');
                                    return href && href.includes('/' + expectedUsername) && !href.includes('/status/');
                                });
                                
                                // Solo procesar si es del usuario correcto
                                if (isMainUser) {
                                    const imgElements = container.querySelectorAll('img[src*="pbs.twimg.com"]');
                                    imgElements.forEach(img => {
                                        if (img.src && 
                                            !img.src.includes('profile_images') && 
                                            !img.src.includes('profile_banners') &&
                                            !img.src.includes('amplify_video_thumb') &&
                                            !img.src.includes('video_thumb') &&
                                            img.width > 100 && img.height > 100) {
                                            images.push({
                                                src: img.src,
                                                username: expectedUsername,
                                                isMainTweet: true
                                            });
                                        }
                                    });
                                }
                            }
                            
                            // Eliminar duplicados y devolver solo las URLs
                            const uniqueImages = [...new Set(images.map(img => img.src))];
                            return uniqueImages;
                        }
                    """, status_url)
                    
                    if tweet_images:
                        status_image_list = []
                        
                        # Procesar TODAS las imágenes encontradas en el tweet (carruseles)
                        for img_index, img_src in enumerate(tweet_images):
                            clean_img_url = URLUtils.clean_image_url_robust(img_src)
                            
                            if clean_img_url:
                                # Verificar duplicados comparando la base de la URL (sin parámetros)
                                is_duplicate = self._is_duplicate_image(clean_img_url, image_urls)
                                
                                if not is_duplicate:
                                    image_urls.append(clean_img_url)
                                    status_image_list.append(clean_img_url)
                                    constructed_count += 1
                                    Logger.info(f"   ✅ [{i}/{len(remaining_status_urls)}] URL construida #{img_index+1}: {clean_img_url}")
                                else:
                                    Logger.info(f"   💾 [{i}/{len(remaining_status_urls)}] URL ya existe #{img_index+1}: {clean_img_url}")
                                    # Aún añadir a la lista del status para mapeo correcto
                                    if clean_img_url in image_urls:
                                        status_image_list.append(clean_img_url)
                        
                        # Guardar mapeo completo para este status (todas las imágenes del usuario correcto)
                        if status_image_list:
                            if len(status_image_list) == 1:
                                status_mappings[status_id] = status_image_list[0]  # String para una sola imagen
                            else:
                                status_mappings[status_id] = status_image_list  # Lista para múltiples imágenes
                            
                            Logger.info(f"   📸 [{i}/{len(remaining_status_urls)}] Status {status_id} mapeado a {len(status_image_list)} imagen(es) del usuario correcto")
                        else:
                            Logger.warning(f"   ⚠️  [{i}/{len(remaining_status_urls)}] No se encontraron imágenes del usuario @{target_username} en este status")
                        
                except Exception as e:
                    Logger.error(f"   ❌ [{i}/{len(remaining_status_urls)}] Error navegando a {status_url}: {e}")
                    continue
                    
            except Exception as e:
                Logger.error(f"   ❌ [{i}/{len(remaining_status_urls)}] Error procesando {item.get('url', 'unknown')}: {e}")
                continue
                
            # Pausa orgánica entre navegaciones para simular comportamiento humano
            if i < len(remaining_status_urls):
                delay = self._get_organic_delay()
                Logger.info(f"   ⏱️  Pausa orgánica: {delay:.2f}s antes de la siguiente URL")
                await asyncio.sleep(delay)
        
        Logger.info(f"   ✅ Método 2 mejorado: {constructed_count} imágenes construidas directamente")
        Logger.info(f"   📸 Se mapearon {len(status_mappings)} status con sus imágenes correspondientes")
        return constructed_count, status_mappings

    def _get_organic_delay(self, base_delay: float = 1.5) -> float:
        """
        Calcula un tiempo de espera orgánico y aleatorio para simular comportamiento humano.
        
        Args:
            base_delay: Tiempo base en segundos (por defecto 1.5s)
            
        Returns:
            Tiempo de espera en segundos con variación aleatoria
        """
        # Variación aleatoria del ±40% del tiempo base
        variation = random.uniform(-0.4, 0.6)  # -40% a +60% para mayor naturalidad
        delay = base_delay * (1 + variation)
        
        # Asegurar que esté dentro del rango deseado (1.0 - 2.5 segundos)
        delay = max(1.0, min(2.5, delay))
        
        # Ocasionalmente agregar pausas más largas (5% de probabilidad)
        if random.random() < 0.05:
            delay += random.uniform(1.0, 3.0)  # Pausa larga ocasional
            Logger.info(f"   ⏱️  Aplicando pausa larga: {delay:.2f}s")
        
        return delay

    def _extract_status_id(self, status_url: str) -> str:
        """Extrae el ID del status desde la URL."""
        try:
            return status_url.split('/status/')[-1].split('?')[0].split('/')[0]
        except Exception:
            return ""

    def _create_correlation_mappings(self, image_urls: list, status_urls: list, existing_mapping: dict):
        """
        MÉTODO DESACTIVADO: Este método causaba mapeos incorrectos.
        La correlación por orden no es confiable cuando hay carruseles de múltiples imágenes.
        """
        Logger.info(f"   ⚠️  Método de correlación desactivado para evitar mapeos incorrectos")
        Logger.info(f"   💡 Solo se usan mapeos explícitos obtenidos de navegación directa")
        return 0
    
    def _is_duplicate_image(self, new_url: str, existing_urls: list[str]) -> bool:
        """
        Verifica si una URL de imagen ya existe en la lista.
        Compara la base de la imagen (sin parámetros) para detectar duplicados.
        """
        try:
            # Extraer la parte base de la nueva URL (sin parámetros)
            new_base = new_url.split('?')[0] if '?' in new_url else new_url
            
            for existing_url in existing_urls:
                # Extraer la parte base de la URL existente
                existing_base = existing_url.split('?')[0] if '?' in existing_url else existing_url
                
                # Comparar las bases
                if new_base == existing_base:
                    return True
                    
            return False
        except Exception:
            return False

    async def _fallback_image_extraction(self, image_status_urls: list[dict], image_urls: list[str], expected_images: int):
        """
        MÉTODO 3: Fallback con extracción alternativa
        """
        Logger.info("   🔄 MÉTODO 3: Fallback con extracción alternativa...")
        
        # Obtener todas las imágenes disponibles en la página con más contexto
        all_page_images = await self.page.evaluate("""
            () => {
                const images = [];
                const imgElements = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                imgElements.forEach(img => {
                    if (img.src && img.src.includes('pbs.twimg.com') && 
                        !img.src.includes('profile_images') && 
                        !img.src.includes('profile_banners')) {
                        
                        // Obtener más contexto sobre la imagen
                        const parentLink = img.closest('a');
                        const tweetContainer = img.closest('article') || img.closest('[data-testid="tweet"]');
                        
                        images.push({
                            src: img.src,
                            alt: img.alt || '',
                            parent_href: parentLink ? parentLink.href : null,
                            has_tweet_container: !!tweetContainer,
                            width: img.naturalWidth || img.width || 0,
                            height: img.naturalHeight || img.height || 0
                        });
                    }
                });
                return images;
            }
        """)
        
        Logger.info(f"   📊 Encontradas {len(all_page_images)} imágenes totales en la página")
        
        # Filtrar imágenes que parecen ser de tweets (no avatares pequeños)
        tweet_images = []
        for img_data in all_page_images:
            # Filtrar por tamaño (evitar avatares pequeños)
            if img_data['width'] > 100 and img_data['height'] > 100:
                tweet_images.append(img_data)
            elif img_data['has_tweet_container']:  # O si está en un contenedor de tweet
                tweet_images.append(img_data)
        
        Logger.info(f"   🎯 Filtradas {len(tweet_images)} imágenes que parecen ser de tweets")
        
        # Añadir imágenes que no estén ya en la lista
        added_count = 0
        for img_data in tweet_images:
            clean_img_url = URLUtils.clean_image_url_robust(img_data['src'])
            if clean_img_url and clean_img_url not in image_urls:
                # Filtrar thumbnails de video que no son imágenes reales
                if 'amplify_video_thumb' not in clean_img_url and 'video_thumb' not in clean_img_url:
                    image_urls.append(clean_img_url)
                    added_count += 1
                    Logger.info(f"   ➕ Imagen alternativa añadida: {clean_img_url}")
                else:
                    Logger.warning(f"   🎬 Thumbnail de video excluido: {clean_img_url}")
                
                # No limitar artificialmente - permitir múltiples imágenes por tweet
                # if len(image_urls) >= expected_images:
                #     Logger.warning(f"   🛑 Límite de {expected_images} imágenes alcanzado")
                #     break
        
        Logger.info(f"   ✅ Método alternativo añadió {added_count} imágenes adicionales")