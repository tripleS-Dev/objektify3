share_js = r"""
        async (items) => {
          const arr = Array.isArray(items) ? items : (items ? [items] : []);
          if (!arr.length) { alert("공유할 파일이 없어요."); return []; }

          const files = [];
          for (const it of arr) {
            const url = (it && typeof it === "object") ? it.url : it;
            const name = (it && typeof it === "object" && it.orig_name) ? it.orig_name : "shared-image";
            if (!url) continue;

            const resp = await fetch(url);
            const blob = await resp.blob();
            files.push(new File([blob], name, { type: blob.type || (it?.mime_type ?? "application/octet-stream") }));
          }

          if (!files.length) { alert("파일을 가져오지 못했어요."); return []; }

          const data = {
            title: "Make your own photo card! Objektify",
            text: "Make your own photo card! [Objektify.xyz](https://objektify.xyz)",
            files
          };

          if (navigator.canShare && navigator.canShare({ files })) {
            try { await navigator.share(data); } catch (e) {}
          } else {
            alert("이 브라우저/환경은 '여러 파일 공유'를 지원하지 않을 수 있어요.");
          }
          return [];
        }
        """
