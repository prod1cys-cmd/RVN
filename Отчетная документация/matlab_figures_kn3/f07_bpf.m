% Рисунок: АЧХ и групповое время запаздывания полосового фильтра ПЧ (Баттерворт)
f0 = 60e6; Bw = 30e6; f = linspace(1e6,500e6,20000); w = 2*pi*f; w0 = 2*pi*f0; bw = 2*pi*Bw;
h = fig_new(16,12);
ord = [3 4 5]; cl = {[0.6 0.6 0.6],'b',[0 0.6 0]}; leg = {};
for k = 1:3
  n = ord(k); p = exp(1i*pi*(2*(1:n)+n-1)/(2*n));      % полюсы НЧ-прототипа
  S = ((1i*w).^2 + w0^2)./(1i*w*bw);
  H = ones(size(S)); for q = 1:n, H = H./(S - p(q)); end
  H = H*prod(-p);
  subplot(2,1,1); hold on; plot(f/1e6, 20*log10(abs(H)), 'Color', cl{k});
  ph = unwrap(angle(H)); gd = -diff(ph)./diff(w);
  subplot(2,1,2); hold on; plot(f(2:end)/1e6, gd*1e9, 'Color', cl{k});
  leg{end+1} = sprintf('n = %d',n);
end
subplot(2,1,1); box on; grid on;
patch([330 350 350 330],[-120 -120 -72 -72],[1 0.8 0.8],'EdgeColor','r');
patch([450 470 470 450],[-120 -120 -72 -72],[1 0.8 0.8],'EdgeColor','r');
patch([50 70 70 50],[-120 -120 5 5],[1 0.9 0.7],'EdgeColor','none','FaceAlpha',0.5);
text(355,-66,'требуемое подавление 72 дБ','Color','r');
xlim([0 500]); ylim([-120 5]); ylabel('|H(f)|, дБ'); xlabel('Частота, МГц');
legend(leg,'Location','northeast');
subplot(2,1,2); box on; grid on;
patch([50 70 70 50],[0 0 40 40],[1 0.9 0.7],'EdgeColor','none','FaceAlpha',0.5);
xlim([30 90]); ylim([0 40]); ylabel('Групповое время запаздывания, нс'); xlabel('Частота, МГц');
fig_save(h,'f07_bpf');
% вывод значений для текста
for n = 3:5
  x = @(ff) (ff.^2-f0^2)./(ff*Bw);
  fprintf('n=%d: A(330)=%.1f A(350)=%.1f A(450)=%.1f A(470)=%.1f dB\n', n, 10*log10(1+x(330e6)^(2*n)), 10*log10(1+x(350e6)^(2*n)), 10*log10(1+x(450e6)^(2*n)), 10*log10(1+x(470e6)^(2*n)));
end
