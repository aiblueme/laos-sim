FROM nginx:alpine

# Copy only the static site files — NOT the Python scripts, raw images, or report
COPY index.html /usr/share/nginx/html/
COPY css/       /usr/share/nginx/html/css/
COPY js/        /usr/share/nginx/html/js/
COPY images/full/   /usr/share/nginx/html/images/full/
COPY images/thumbs/ /usr/share/nginx/html/images/thumbs/
